#!/usr/bin/env python3
"""
Demonstrate SWE-bench instance to agent task conversion

This script shows how SWE-bench instances are converted into
agent-readable task descriptions.
"""

from swebench.loader import load_dataset
from swebench.adapter import convert_to_task


def main():
    print("Loading SWE-bench Lite dataset...")
    dataset = load_dataset("SWE-bench/SWE-bench_Lite", split="test")
    
    print(f"✓ Loaded {len(dataset)} instances\n")
    print("=" * 80)
    print("TASK CONVERSION EXAMPLES")
    print("=" * 80)
    
    # Show conversion for first 3 instances
    for i, instance in enumerate(dataset[:3], 1):
        print(f"\n{'#'*80}")
        print(f"# Example {i}: {instance['instance_id']}")
        print(f"{'#'*80}\n")
        
        # Convert to task
        task = convert_to_task(instance)
        
        print("Original Instance:")
        print(f"  Repository: {instance['repo']}")
        print(f"  Base Commit: {instance['base_commit'][:12]}...")
        print(f"  Problem Statement (first 100 chars):")
        print(f"    {instance['problem_statement'][:100]}...")
        
        print(f"\n{'─'*80}")
        print("Converted Agent Task:")
        print(f"{'─'*80}")
        print(task)
        print(f"{'─'*80}\n")


if __name__ == "__main__":
    main()
