"""
General utilities for AlphaFold MCP scripts.

These functions provide common functionality for command construction,
validation, and configuration management.
"""

from pathlib import Path
from typing import Union, Dict, List, Optional, Any
import json


def build_alphafold_command(
    fasta_path: Union[str, Path],
    output_dir: Union[str, Path],
    alphafold_script: Union[str, Path],
    data_dir: Optional[Union[str, Path]] = None,
    model_preset: str = 'monomer',
    db_preset: str = 'reduced_dbs',
    max_template_date: str = '2022-01-01',
    num_predictions_per_model: Optional[int] = None,
    **kwargs
) -> List[str]:
    """
    Build AlphaFold command line arguments.

    Args:
        fasta_path: Input FASTA file
        output_dir: Output directory
        alphafold_script: Path to run_alphafold.py
        data_dir: AlphaFold databases directory (optional)
        model_preset: Model configuration
        db_preset: Database preset
        max_template_date: Maximum template date
        num_predictions_per_model: Number of predictions (for multimer)
        **kwargs: Additional command line arguments

    Returns:
        List of command parts ready for subprocess
    """
    cmd_parts = [
        'python',
        str(alphafold_script),
        f'--fasta_paths={fasta_path}',
        f'--output_dir={output_dir}',
        f'--model_preset={model_preset}',
        f'--db_preset={db_preset}',
        f'--max_template_date={max_template_date}',
    ]

    if data_dir:
        cmd_parts.append(f'--data_dir={data_dir}')

    if num_predictions_per_model is not None:
        cmd_parts.append(f'--num_predictions_per_model={num_predictions_per_model}')

    # Add any additional arguments
    for key, value in kwargs.items():
        if value is not None:
            # Convert python parameter names to command line format
            cli_key = key.replace('_', '-')
            if isinstance(value, bool):
                if value:
                    cmd_parts.append(f'--{cli_key}')
            else:
                cmd_parts.append(f'--{cli_key}={value}')

    return cmd_parts


def load_config(config_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Load configuration from JSON file.

    Args:
        config_path: Path to config file

    Returns:
        Configuration dictionary
    """
    config_path = Path(config_path)
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, 'r') as f:
        return json.load(f)


def save_config(config: Dict[str, Any], config_path: Union[str, Path]) -> None:
    """
    Save configuration to JSON file.

    Args:
        config: Configuration dictionary
        config_path: Output file path
    """
    config_path = Path(config_path)
    config_path.parent.mkdir(parents=True, exist_ok=True)

    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)


def validate_fasta_file(fasta_path: Union[str, Path]) -> bool:
    """
    Validate that file exists and appears to be a FASTA file.

    Args:
        fasta_path: Path to FASTA file

    Returns:
        True if valid
    """
    fasta_path = Path(fasta_path)

    if not fasta_path.exists():
        return False

    # Check if file has FASTA content
    try:
        with open(fasta_path, 'r') as f:
            first_line = f.readline().strip()
            return first_line.startswith('>')
    except Exception:
        return False


def estimate_resources(sequence_length: int, is_multimer: bool = False) -> Dict[str, str]:
    """
    Estimate computational resources needed for prediction.

    Args:
        sequence_length: Total number of amino acids
        is_multimer: True if multimer prediction

    Returns:
        Dictionary with resource estimates
    """
    # Base estimates (very rough)
    if sequence_length <= 100:
        cpu_time = "10-30 minutes"
        memory = "8-16 GB"
    elif sequence_length <= 300:
        cpu_time = "1-3 hours"
        memory = "16-32 GB"
    elif sequence_length <= 1000:
        cpu_time = "6-24 hours"
        memory = "32-64 GB"
    else:
        cpu_time = "1-7 days"
        memory = "64-128 GB"

    # Multimer complexes need more resources
    if is_multimer:
        cpu_time = f"{cpu_time} (2-10x longer for multimer)"
        memory = f"{memory} (may need more for large complexes)"

    return {
        "estimated_cpu_time": cpu_time,
        "estimated_memory": memory,
        "disk_space": "2.6TB (full databases) or 600GB (reduced databases)",
        "gpu_recommended": "Yes (optional but significantly faster)"
    }


def get_default_paths() -> Dict[str, Path]:
    """
    Get default paths for AlphaFold components.

    Returns:
        Dictionary of default paths
    """
    script_dir = Path(__file__).parent.parent
    mcp_root = script_dir.parent

    return {
        "mcp_root": mcp_root,
        "scripts_dir": script_dir,
        "repo_dir": mcp_root / "repo",
        "alphafold_script": mcp_root / "repo" / "alphafold" / "run_alphafold.py",
        "examples_data": mcp_root / "examples" / "data",
        "configs_dir": mcp_root / "configs",
        "results_dir": mcp_root / "results"
    }


def create_sample_sequences() -> Dict[str, str]:
    """
    Create sample protein sequences for testing.

    Returns:
        Dictionary of sample sequences
    """
    return {
        "insulin_chain_a": "GIVEQCCTSICSLYQLENYCN",
        "insulin_chain_b": "FVNQHLCGSHLVEALYLVCGERGFFYTPKT",
        "small_protein": "MALWMRLLPLLALLALWGPDPAAAFVNQHLCGSHLVEALYLVCGERGFFYTPKT",
        "lysozyme": "KVFGRCELAAAMKRHGLDNYRGYSLGNWVCAAKFESNFNTQATNRNTDGSTDYGILQINSRWWCNDGRTPGSRNLCNIPCSALLSSDITASVNCAKKIVSDGNGMNAWVAWRNRCKGTDVQAWIRGCRL"
    }