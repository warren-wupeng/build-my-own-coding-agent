#!/usr/bin/env python3
"""
Display examples of SWE-bench dataset instances

This script loads a few instances from SWE-bench Lite and displays
their structure and content.
"""

import json
from swebench.loader import load_dataset, validate_instance


def format_instance(instance, show_full=False):
    """Format an instance for display"""
    output = []
    output.append("=" * 80)
    output.append(f"Instance ID: {instance['instance_id']}")
    output.append(f"Repository: {instance['repo']}")
    output.append(f"Base Commit: {instance['base_commit'][:12]}...")
    output.append("-" * 80)
    
    # Problem Statement
    problem = instance['problem_statement']
    if len(problem) > 500 and not show_full:
        problem = problem[:500] + "...\n[truncated]"
    output.append("Problem Statement:")
    output.append(problem)
    output.append("-" * 80)
    
    # Test Information
    output.append(f"Tests to Fix (FAIL_TO_PASS): {len(instance['FAIL_TO_PASS'])} tests")
    if instance['FAIL_TO_PASS']:
        for i, test in enumerate(instance['FAIL_TO_PASS'][:3], 1):
            output.append(f"  {i}. {test}")
        if len(instance['FAIL_TO_PASS']) > 3:
            output.append(f"  ... and {len(instance['FAIL_TO_PASS']) - 3} more")
    
    output.append(f"Tests to Maintain (PASS_TO_PASS): {len(instance['PASS_TO_PASS'])} tests")
    if instance['PASS_TO_PASS']:
        for i, test in enumerate(instance['PASS_TO_PASS'][:3], 1):
            output.append(f"  {i}. {test}")
        if len(instance['PASS_TO_PASS']) > 3:
            output.append(f"  ... and {len(instance['PASS_TO_PASS']) - 3} more")
    
    output.append("-" * 80)
    
    # Patch Information
    patch = instance.get('patch', '')
    patch_lines = len(patch.split('\n')) if patch else 0
    output.append(f"Gold Patch: {patch_lines} lines")
    if patch and show_full:
        output.append("Patch Preview:")
        output.append(patch[:300] + "..." if len(patch) > 300 else patch)
    
    test_patch = instance.get('test_patch', '')
    test_patch_lines = len(test_patch.split('\n')) if test_patch else 0
    output.append(f"Test Patch: {test_patch_lines} lines")
    
    return "\n".join(output)


def main():
    print("Loading SWE-bench Lite dataset from HuggingFace...")
    print("This may take a moment on first run...\n")
    
    try:
        # Load dataset
        dataset = load_dataset("SWE-bench/SWE-bench_Lite", split="test")
        
        print(f"✓ Successfully loaded {len(dataset)} instances\n")
        
        # Display first 3 instances
        print(f"\n{'='*80}")
        print("SHOWING FIRST 3 INSTANCES")
        print(f"{'='*80}\n")
        
        for i, instance in enumerate(dataset[:3], 1):
            print(f"\n{'#'*80}")
            print(f"# Example {i} of {len(dataset)}")
            print(f"{'#'*80}\n")
            print(format_instance(instance, show_full=False))
            print()
        
        # Show summary statistics
        print(f"\n{'='*80}")
        print("DATASET SUMMARY")
        print(f"{'='*80}\n")
        
        repos = {}
        total_f2p = 0
        total_p2p = 0
        
        for instance in dataset:
            repo = instance['repo']
            repos[repo] = repos.get(repo, 0) + 1
            total_f2p += len(instance['FAIL_TO_PASS'])
            total_p2p += len(instance['PASS_TO_PASS'])
        
        print(f"Total Instances: {len(dataset)}")
        print(f"Unique Repositories: {len(repos)}")
        print(f"\nRepositories:")
        for repo, count in sorted(repos.items(), key=lambda x: x[1], reverse=True):
            print(f"  - {repo}: {count} instances")
        
        print(f"\nTest Statistics:")
        print(f"  Total FAIL_TO_PASS tests: {total_f2p}")
        print(f"  Total PASS_TO_PASS tests: {total_p2p}")
        print(f"  Average FAIL_TO_PASS per instance: {total_f2p / len(dataset):.1f}")
        print(f"  Average PASS_TO_PASS per instance: {total_p2p / len(dataset):.1f}")
        
        # Show a detailed example of one instance
        print(f"\n{'='*80}")
        print("DETAILED EXAMPLE (First Instance)")
        print(f"{'='*80}\n")
        
        first_instance = dataset[0]
        print(format_instance(first_instance, show_full=True))
        
        # Show instance structure
        print(f"\n{'='*80}")
        print("INSTANCE DATA STRUCTURE")
        print(f"{'='*80}\n")
        print("Available fields:")
        for key in first_instance.keys():
            value = first_instance[key]
            if isinstance(value, str):
                preview = value[:50] + "..." if len(value) > 50 else value
                print(f"  - {key}: {type(value).__name__} (length: {len(value)})")
                print(f"    Preview: {preview}")
            elif isinstance(value, list):
                print(f"  - {key}: {type(value).__name__} (length: {len(value)})")
                if value:
                    print(f"    First item: {value[0]}")
            else:
                print(f"  - {key}: {type(value).__name__} = {value}")
        
    except Exception as e:
        print(f"Error loading dataset: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
