"""
SWE-bench inference interface

This module provides the main interface for running inference on SWE-bench instances.
It orchestrates the complete pipeline: load → convert → execute → extract → format.
"""

import json
import logging
import os
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional

from swebench.adapter import convert_to_task
from swebench.patch_generator import (
    extract_file_modifications,
    generate_patch,
    generate_git_diff,
    extract_patch_from_messages
)

logger = logging.getLogger(__name__)


class InferenceError(Exception):
    """Custom exception for inference failures."""
    pass


def _prepare_repository_from_cache(
    repo: str,
    base_commit: str,
    workspace_path: Path
) -> Optional[Path]:
    """
    Prepare repository in workspace from cache or clone if not available.
    
    Args:
        repo: Repository name in format "owner/name"
        base_commit: Git commit hash to checkout
        workspace_path: Path to agent workspace directory
    
    Returns:
        Path to repository directory in workspace, or None if preparation failed
    """
    repo_name = repo.split("/")[-1]  # Extract repository name
    repo_work_path = workspace_path / repo_name
    
    # Try to use cached repository
    cache_repo_name = repo.replace("/", "_")
    cache_path = Path(f"/cache/repos/{cache_repo_name}")
    
    if cache_path.exists():
        logger.info(f"Using cached repository: {cache_path}")
        try:
            # Copy repository to workspace (faster than cloning)
            if repo_work_path.exists():
                shutil.rmtree(repo_work_path)
            shutil.copytree(cache_path, repo_work_path)
            
            # Reset to the correct commit
            subprocess.run(
                ["git", "reset", "--hard", base_commit],
                cwd=repo_work_path,
                check=True,
                capture_output=True
            )
            logger.info(f"Repository prepared at {repo_work_path} (commit: {base_commit[:12]})")
            return repo_work_path
        except (subprocess.CalledProcessError, OSError) as e:
            logger.warning(f"Failed to prepare repository from cache: {e}")
            # Fall through to clone from GitHub
    else:
        logger.info(f"Cache not found for {repo}, will clone from GitHub if needed")
    
    # Fallback: clone from GitHub (if network available)
    # Note: This is a fallback, but in containerized environment might not have network
    # or might be slow. The cache should be preferred.
    try:
        if not repo_work_path.exists():
            repo_url = f"https://github.com/{repo}.git"
            logger.info(f"Cloning repository from GitHub: {repo_url}")
            subprocess.run(
                ["git", "clone", repo_url, str(repo_work_path)],
                check=True,
                capture_output=True,
                timeout=300  # 5 minute timeout
            )
        
        # Reset to the correct commit
        subprocess.run(
            ["git", "reset", "--hard", base_commit],
            cwd=repo_work_path,
            check=True,
            capture_output=True
        )
        logger.info(f"Repository cloned and prepared at {repo_work_path} (commit: {base_commit[:12]})")
        return repo_work_path
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError) as e:
        logger.warning(f"Failed to clone repository: {e}")
        return None


def run_inference(
    instance: Dict[str, Any],
    agent_core: Any,
    model_name_or_path: str = "my-coding-agent-v5"
) -> Dict[str, Any]:
    """
    Run inference on a single SWE-bench instance.
    
    This function orchestrates the complete pipeline:
    1. Convert instance to task string
    2. Execute task with agent
    3. Extract file modifications from agent messages
    4. Generate git diff patch
    5. Format as SWE-bench prediction
    
    Args:
        instance: SWE-bench instance dictionary
        agent_core: AgentCore instance to execute the task
        model_name_or_path: Model identifier for the prediction
    
    Returns:
        Dictionary with keys:
            - instance_id: Instance identifier
            - model_name_or_path: Model identifier
            - model_patch: Git diff patch string
    
    Raises:
        InferenceError: If inference fails
        ValueError: If instance is invalid
    """
    try:
        # Validate instance
        if not instance or "instance_id" not in instance:
            raise ValueError("Invalid instance: missing instance_id")
        
        instance_id = instance["instance_id"]
        logger.info(f"Running inference on instance: {instance_id}")
        
        # Prepare repository in agent workspace
        repo = instance.get("repo", "")
        base_commit = instance.get("base_commit", "")
        
        # Switch to agent workspace directory (isolated from code directory)
        workspace_dir = os.getenv('AGENT_WORKSPACE', '/agent-workspace')
        workspace_path = Path(workspace_dir)
        workspace_path.mkdir(parents=True, exist_ok=True)
        
        # Try to use cached repository if available
        repo_work_path = None
        if repo and base_commit:
            repo_work_path = _prepare_repository_from_cache(
                repo, base_commit, workspace_path
            )
        
        original_cwd = os.getcwd()
        try:
            # Change to repository directory if available, otherwise just workspace
            if repo_work_path and repo_work_path.exists():
                os.chdir(repo_work_path)
                logger.info(f"Changed to repository workspace: {repo_work_path}")
            else:
                os.chdir(workspace_path)
                logger.info(f"Changed to agent workspace: {workspace_path} (from {original_cwd})")
            
            # Step 1: Convert instance to task
            try:
                task = convert_to_task(instance)
            except ValueError as e:
                raise InferenceError(f"Failed to convert instance to task: {e}") from e
            
            # Step 2: Initialize agent tools (if not already initialized)
            if not agent_core.tools:
                agent_core.initialize_tools()
            
            # Step 3: Execute task with agent
            try:
                logger.info(f"Starting agent task execution for instance {instance_id}...")
                success = agent_core.execute_task(task)
                if success:
                    logger.info(f"Task execution completed successfully (returned True) for instance {instance_id}")
                else:
                    logger.warning(
                        f"Task execution did not complete successfully (returned False) for instance {instance_id}. "
                        f"This could mean: max_steps reached, unknown finish_reason, or execution error."
                    )
            except Exception as e:
                logger.error(f"Error during task execution for instance {instance_id}: {e}", exc_info=True)
                # Continue to extract patch even if execution had issues
            
            # Step 4: Extract patch from agent messages
            messages = agent_core.messages if hasattr(agent_core, 'messages') else []
            
            # Step 5: Generate patch using extract_patch_from_messages
            # This function handles both extraction and patch generation
            patch = extract_patch_from_messages(messages)
            
            if not patch:
                logger.warning(f"No file modifications found for instance {instance_id}")
            
            # Step 6: Format as SWE-bench prediction
            prediction = {
                "instance_id": instance_id,
                "model_name_or_path": model_name_or_path,
                "model_patch": patch
            }
            
            logger.info(f"Inference completed for instance {instance_id}, patch size: {len(patch)} chars")
            return prediction
            
        finally:
            # Always restore original working directory
            os.chdir(original_cwd)
            logger.info(f"Restored working directory: {original_cwd}")
        
    except Exception as e:
        logger.error(f"Inference failed for instance {instance.get('instance_id', 'unknown')}: {e}")
        raise InferenceError(f"Inference failed: {e}") from e


def generate_predictions_file(
    predictions: List[Dict[str, Any]],
    output_path: str,
    append: bool = False
) -> None:
    """
    Generate a predictions file in SWE-bench JSONL format.
    
    Args:
        predictions: List of prediction dictionaries, each with:
            - instance_id: Instance identifier
            - model_name_or_path: Model identifier
            - model_patch: Git diff patch string
        output_path: Path to output JSONL file
        append: If True, append to existing file; if False, overwrite
    
    Raises:
        ValueError: If predictions are invalid
        IOError: If file cannot be written
    """
    # Validate predictions
    required_fields = ["instance_id", "model_name_or_path", "model_patch"]
    
    for i, pred in enumerate(predictions):
        missing_fields = [field for field in required_fields if field not in pred]
        if missing_fields:
            raise ValueError(
                f"Prediction at index {i} missing required fields: {', '.join(missing_fields)}"
            )
        
        # Validate types
        if not isinstance(pred["instance_id"], str):
            raise ValueError(f"Prediction at index {i}: instance_id must be a string")
        if not isinstance(pred["model_name_or_path"], str):
            raise ValueError(f"Prediction at index {i}: model_name_or_path must be a string")
        if not isinstance(pred["model_patch"], str):
            raise ValueError(f"Prediction at index {i}: model_patch must be a string")
    
    # Write predictions to file
    output_file = Path(output_path)
    mode = "a" if append and output_file.exists() else "w"
    
    try:
        with open(output_file, mode, encoding="utf-8") as f:
            for pred in predictions:
                json_line = json.dumps(pred, ensure_ascii=False)
                f.write(json_line + "\n")
        
        logger.info(f"Generated predictions file: {output_path} with {len(predictions)} predictions")
    except IOError as e:
        raise IOError(f"Failed to write predictions file {output_path}: {e}") from e


def run_batch_inference(
    instances: List[Dict[str, Any]],
    agent_core: Any,
    model_name_or_path: str = "my-coding-agent-v5",
    output_path: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Run inference on multiple SWE-bench instances.
    
    Args:
        instances: List of SWE-bench instance dictionaries
        agent_core: AgentCore instance to execute tasks
        model_name_or_path: Model identifier for predictions
        output_path: Optional path to save predictions file
    
    Returns:
        List of prediction dictionaries
    
    Raises:
        InferenceError: If batch inference fails
    """
    predictions = []
    
    for i, instance in enumerate(instances):
        instance_id = instance.get("instance_id", f"unknown-{i}")
        logger.info(f"Processing instance {i+1}/{len(instances)}: {instance_id}")
        
        try:
            prediction = run_inference(instance, agent_core, model_name_or_path)
            predictions.append(prediction)
            
            # Optionally save incrementally
            if output_path:
                generate_predictions_file([prediction], output_path, append=True)
                
        except Exception as e:
            logger.error(f"Failed to process instance {instance_id}: {e}")
            # Continue with next instance
            # Optionally, add empty prediction
            predictions.append({
                "instance_id": instance_id,
                "model_name_or_path": model_name_or_path,
                "model_patch": ""
            })
    
    # Save final predictions file if output_path provided and not already saved incrementally
    if output_path and not predictions:
        # Only save if we have predictions and haven't saved incrementally
        # (In practice, you might want to save even if empty)
        pass
    
    logger.info(f"Batch inference completed: {len(predictions)}/{len(instances)} instances processed")
    return predictions
