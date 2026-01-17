#!/usr/bin/env python3
"""
Display SWE-bench dataset instances in JSON format

This script loads instances and displays them as formatted JSON
for easier inspection.
"""

import json
from swebench.loader import load_dataset


def main():
    print("Loading SWE-bench Lite dataset...\n")
    
    dataset = load_dataset("SWE-bench/SWE-bench_Lite", split="test")
    
    print(f"✓ Loaded {len(dataset)} instances\n")
    print("=" * 80)
    print("EXAMPLE 1: First Instance (Full JSON)")
    print("=" * 80)
    
    # Show first instance as JSON
    first = dataset[0]
    print(json.dumps(first, indent=2, ensure_ascii=False))
    
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Summary of First 5 Instances")
    print("=" * 80)
    
    # Show summary of first 5
    for i, instance in enumerate(dataset[:5], 1):
        print(f"\n--- Instance {i}: {instance['instance_id']} ---")
        print(f"Repository: {instance['repo']}")
        print(f"Base Commit: {instance['base_commit'][:12]}...")
        print(f"Problem Statement (first 200 chars):")
        print(f"  {instance['problem_statement'][:200]}...")
        print(f"FAIL_TO_PASS tests: {len(instance['FAIL_TO_PASS'])}")
        print(f"PASS_TO_PASS tests: {len(instance['PASS_TO_PASS'])}")
        print(f"Patch size: {len(instance['patch'])} chars")
        print(f"Test patch size: {len(instance['test_patch'])} chars")


if __name__ == "__main__":
    main()
