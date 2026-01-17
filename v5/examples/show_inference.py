#!/usr/bin/env python3
"""
Example: Using SWE-bench inference interface

This example demonstrates how to use the inference interface to:
1. Load a SWE-bench instance
2. Run inference with an agent
3. Generate predictions file
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from swebench.loader import load_dataset
from swebench.inference import run_inference, generate_predictions_file, run_batch_inference
from core.agent_core import AgentCore


def main():
    print("=" * 80)
    print("SWE-bench Inference Interface Example")
    print("=" * 80)
    print()
    
    # Example 1: Load a single instance from dataset
    print("#" * 80)
    print("# Example 1: Load and process a single instance")
    print("#" * 80)
    print()
    
    try:
        # Load a small subset for testing
        instances = load_dataset("SWE-bench/SWE-bench_Lite", split="test", instance_ids=None)
        if not instances:
            print("No instances loaded. Using mock instance for demonstration.")
            instance = {
                "instance_id": "example__repo-1",
                "repo": "example/repo",
                "base_commit": "abc123def456",
                "problem_statement": "Fix a bug in the code",
                "patch": "",
                "test_patch": "",
                "FAIL_TO_PASS": [],
                "PASS_TO_PASS": []
            }
        else:
            instance = instances[0]
            print(f"Loaded instance: {instance['instance_id']}")
            print(f"Repository: {instance['repo']}")
            print(f"Base commit: {instance['base_commit']}")
            print(f"Problem statement (first 100 chars): {instance['problem_statement'][:100]}...")
            print()
    except Exception as e:
        print(f"Error loading dataset: {e}")
        print("Using mock instance for demonstration.")
        instance = {
            "instance_id": "example__repo-1",
            "repo": "example/repo",
            "base_commit": "abc123def456",
            "problem_statement": "Fix a bug in the code",
            "patch": "",
            "test_patch": "",
            "FAIL_TO_PASS": [],
            "PASS_TO_PASS": []
        }
    
    # Example 2: Initialize agent and run inference
    print("#" * 80)
    print("# Example 2: Run inference with agent")
    print("#" * 80)
    print()
    
    print("Initializing agent...")
    agent = AgentCore()
    agent.initialize_tools()
    
    print("Running inference...")
    try:
        prediction = run_inference(instance, agent, model_name_or_path="my-coding-agent-v5")
        
        print(f"✓ Inference completed!")
        print(f"  Instance ID: {prediction['instance_id']}")
        print(f"  Model: {prediction['model_name_or_path']}")
        print(f"  Patch size: {len(prediction['model_patch'])} characters")
        
        if prediction['model_patch']:
            print(f"  Patch preview (first 200 chars):")
            print(f"  {prediction['model_patch'][:200]}...")
        else:
            print("  No patch generated (empty)")
        print()
    except Exception as e:
        print(f"✗ Inference failed: {e}")
        print()
    
    # Example 3: Generate predictions file
    print("#" * 80)
    print("# Example 3: Generate predictions file")
    print("#" * 80)
    print()
    
    # Create sample predictions
    sample_predictions = [
        {
            "instance_id": "example__repo-1",
            "model_name_or_path": "my-coding-agent-v5",
            "model_patch": "diff --git a/example.py b/example.py\n--- a/example.py\n+++ b/example.py\n@@ -1 +1 @@\n-old code\n+new code\n"
        },
        {
            "instance_id": "example__repo-2",
            "model_name_or_path": "my-coding-agent-v5",
            "model_patch": ""
        }
    ]
    
    output_file = "example_predictions.jsonl"
    try:
        generate_predictions_file(sample_predictions, output_file)
        print(f"✓ Generated predictions file: {output_file}")
        print(f"  Number of predictions: {len(sample_predictions)}")
        
        # Show file contents
        with open(output_file, 'r') as f:
            lines = f.readlines()
            print(f"  File has {len(lines)} lines")
            print()
            print("  First prediction:")
            import json
            pred = json.loads(lines[0])
            print(f"    Instance ID: {pred['instance_id']}")
            print(f"    Model: {pred['model_name_or_path']}")
            print(f"    Patch: {pred['model_patch'][:50]}..." if pred['model_patch'] else "    Patch: (empty)")
    except Exception as e:
        print(f"✗ Failed to generate predictions file: {e}")
    
    print()
    print("=" * 80)
    print("Example completed!")
    print("=" * 80)


if __name__ == "__main__":
    main()
