"""
SWE-bench instance to agent task adapter

This module converts SWE-bench dataset instances into task descriptions
that can be understood and executed by the coding agent.
"""

from typing import Dict, Any, Optional


# Default task template
DEFAULT_TASK_TEMPLATE = """Repository: {repo}
Issue: {problem_statement}
Base commit: {base_commit}

Please analyze the issue and generate a patch to fix it.
You have access to the codebase at the base commit.
"""


def convert_to_task(instance: Dict[str, Any], template: Optional[str] = None) -> str:
    """
    Convert a SWE-bench instance to an agent task string.
    
    Args:
        instance: SWE-bench instance dictionary
        template: Optional custom task template. If None, uses default template.
                  Template should use {repo}, {problem_statement}, {base_commit} placeholders.
    
    Returns:
        Formatted task string for the agent
    
    Raises:
        ValueError: If required fields are missing
    """
    # Validate required fields
    required_fields = ["repo", "base_commit", "problem_statement"]
    missing_fields = [field for field in required_fields if field not in instance]
    
    if missing_fields:
        raise ValueError(f"Instance missing required fields: {', '.join(missing_fields)}")
    
    # Use provided template or default
    task_template = template if template is not None else DEFAULT_TASK_TEMPLATE
    
    # Extract and format fields
    repo = instance.get("repo", "")
    base_commit = instance.get("base_commit", "")
    problem_statement = instance.get("problem_statement", "")
    
    # Handle empty problem statement
    if not problem_statement:
        problem_statement = "No description provided"
    
    # Format the task
    try:
        task = task_template.format(
            repo=repo,
            base_commit=base_commit,
            problem_statement=problem_statement
        )
    except KeyError as e:
        raise ValueError(f"Template contains unknown placeholder: {e}")
    
    # Clean up the task (remove excessive whitespace)
    task = task.strip()
    
    return task


def validate_task(task: str) -> bool:
    """
    Validate that a task string is well-formed.
    
    Args:
        task: Task string to validate
    
    Returns:
        True if task is valid
    
    Raises:
        ValueError: If task is invalid
    """
    if not isinstance(task, str):
        raise ValueError("Task must be a string")
    
    if not task or not task.strip():
        raise ValueError("Task cannot be empty")
    
    if len(task) < 10:
        raise ValueError("Task is too short to be meaningful")
    
    return True
