"""
SWE-bench dataset loader module

This module provides functions to load SWE-bench datasets from HuggingFace
or local files, validate instances, and filter by instance_id.
"""

from pathlib import Path
from typing import List, Dict, Any, Optional, Union
from datasets import Dataset, load_dataset as hf_load_dataset, load_from_disk
import json
import logging

logger = logging.getLogger(__name__)

# Required fields for a valid SWE-bench instance
REQUIRED_FIELDS = [
    "instance_id",
    "repo",
    "base_commit",
    "problem_statement",
    "patch",
    "test_patch",
    "FAIL_TO_PASS",
    "PASS_TO_PASS",
]

# Dataset name mappings
DATASET_NAME_MAPPINGS = {
    "swe-bench": "SWE-bench/SWE-bench",
    "swebench": "SWE-bench/SWE-bench",
    "swe_bench": "SWE-bench/SWE-bench",
    "swe-bench-lite": "SWE-bench/SWE-bench_Lite",
    "swebench-lite": "SWE-bench/SWE-bench_Lite",
    "swe_bench_lite": "SWE-bench/SWE-bench_Lite",
    "swe-bench_lite": "SWE-bench/SWE-bench_Lite",
    "lite": "SWE-bench/SWE-bench_Lite",
}


def load_dataset(
    name: str,
    split: str = "test",
    instance_ids: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """
    Load SWE-bench dataset from HuggingFace or local file.
    
    Args:
        name: Dataset name (HuggingFace identifier or local file path)
        split: Dataset split to load (default: "test")
        instance_ids: Optional list of instance IDs to filter by
    
    Returns:
        List of dataset instances (dictionaries)
    
    Raises:
        ValueError: If dataset name is invalid or file format is unsupported
        FileNotFoundError: If local file doesn't exist
        ConnectionError: If network error occurs when loading from HuggingFace
    """
    # Load from local JSON/JSONL file
    if name.endswith(".json"):
        dataset = _load_from_json(name)
    elif name.endswith(".jsonl"):
        dataset = _load_from_jsonl(name)
    else:
        # Load from HuggingFace Datasets
        dataset = _load_from_huggingface(name, split)
    
    # Filter by instance_ids if provided
    if instance_ids:
        dataset = filter_instances(dataset, instance_ids)
    
    return dataset


def _load_from_json(file_path: str) -> List[Dict[str, Any]]:
    """Load dataset from local JSON file"""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"JSON file not found: {file_path}")
    
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if not isinstance(data, list):
        raise ValueError(f"JSON file must contain a list of instances, got {type(data)}")
    
    return data


def _load_from_jsonl(file_path: str) -> List[Dict[str, Any]]:
    """Load dataset from local JSONL file"""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"JSONL file not found: {file_path}")
    
    dataset = []
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                dataset.append(json.loads(line))
    
    return dataset


def _load_from_huggingface(name: str, split: str) -> List[Dict[str, Any]]:
    """Load dataset from HuggingFace"""
    # Normalize dataset name
    normalized_name = DATASET_NAME_MAPPINGS.get(name.lower(), name)
    
    try:
        # Try loading from disk cache first
        if (Path(normalized_name) / split / "dataset_info.json").exists():
            dataset = load_from_disk(Path(normalized_name) / split)
        else:
            # Load from HuggingFace
            dataset = hf_load_dataset(normalized_name, split=split)
        
        # Convert Dataset to list of dicts
        if isinstance(dataset, Dataset):
            return list(dataset)
        return dataset
    
    except Exception as e:
        if "Connection" in str(type(e).__name__) or "network" in str(e).lower():
            raise ConnectionError(f"Network error loading dataset {name}: {e}") from e
        raise ValueError(f"Failed to load dataset {name}: {e}") from e


def validate_instance(instance: Dict[str, Any]) -> bool:
    """
    Validate that an instance contains all required fields.
    
    Args:
        instance: Instance dictionary to validate
    
    Returns:
        True if instance is valid
    
    Raises:
        ValueError: If required fields are missing
    """
    if not isinstance(instance, dict):
        raise ValueError(f"Instance must be a dictionary, got {type(instance)}")
    
    if not instance:
        raise ValueError("Instance cannot be empty")
    
    missing_fields = [field for field in REQUIRED_FIELDS if field not in instance]
    
    if missing_fields:
        raise ValueError(
            f"Instance missing required fields: {', '.join(missing_fields)}. "
            f"Required fields: {', '.join(REQUIRED_FIELDS)}"
        )
    
    return True


def filter_instances(
    dataset: List[Dict[str, Any]],
    instance_ids: List[str]
) -> List[Dict[str, Any]]:
    """
    Filter dataset by instance IDs.
    
    Args:
        dataset: List of instances
        instance_ids: List of instance IDs to filter by
    
    Returns:
        Filtered list of instances
    
    Raises:
        ValueError: If any instance_id is not found in the dataset
    """
    instance_ids_set = set(instance_ids)
    dataset_ids = {inst.get("instance_id") for inst in dataset}
    
    # Check for missing IDs
    missing_ids = instance_ids_set - dataset_ids
    if missing_ids:
        raise ValueError(
            f"Some instance IDs not found in dataset: {', '.join(sorted(missing_ids))}"
        )
    
    # Filter dataset
    filtered = [inst for inst in dataset if inst.get("instance_id") in instance_ids_set]
    
    return filtered
