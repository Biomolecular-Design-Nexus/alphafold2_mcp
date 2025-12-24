#!/usr/bin/env python3
"""
Script: monomer_prediction.py
Description: Predict single protein structure using AlphaFold2

Original Use Case: examples/use_case_1_monomer_prediction.py
Dependencies Removed: None (all dependencies inlined or use shared lib)

Usage:
    python scripts/monomer_prediction.py --input <input_file> --output <output_dir>

Example:
    python scripts/monomer_prediction.py --input examples/data/monomer.fasta --output results/monomer_pred
"""

# ==============================================================================
# Minimal Imports (only essential packages)
# ==============================================================================
import argparse
import json
import sys
from pathlib import Path
from typing import Union, Optional, Dict, Any

# Add local lib to path
sys.path.insert(0, str(Path(__file__).parent))
from lib.io import load_fasta, analyze_fasta_content, ensure_directory, save_fasta
from lib.utils import build_alphafold_command, load_config, estimate_resources, get_default_paths, create_sample_sequences

# ==============================================================================
# Configuration (extracted from use case)
# ==============================================================================
DEFAULT_CONFIG = {
    "model_preset": "monomer",
    "db_preset": "reduced_dbs",
    "max_template_date": "2022-01-01",
    "demo_mode": True,
    "create_sample_if_missing": True,
    "sample_sequence": "insulin_chain_a"
}

# ==============================================================================
# Core Sample Data Creation (inlined from use case)
# ==============================================================================
def create_sample_fasta(output_path: Path, sequence_name: str = "insulin_chain_a") -> None:
    """Create a sample FASTA file for testing. Inlined from use_case_1."""

    sample_sequences = create_sample_sequences()

    if sequence_name not in sample_sequences:
        sequence_name = "insulin_chain_a"

    sequence = sample_sequences[sequence_name]

    # Create FASTA content
    sequences = {f"{sequence_name}|Example protein for AlphaFold prediction": sequence}
    save_fasta(sequences, output_path)
    print(f"Created sample FASTA file: {output_path}")

# ==============================================================================
# Core Function (main logic extracted from use case)
# ==============================================================================
def run_monomer_prediction(
    input_file: Union[str, Path],
    output_dir: Optional[Union[str, Path]] = None,
    config: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Main function for AlphaFold2 monomer structure prediction.

    Args:
        input_file: Path to input FASTA file
        output_dir: Path to output directory (optional)
        config: Configuration dict (uses DEFAULT_CONFIG if not provided)
        **kwargs: Override specific config parameters

    Returns:
        Dict containing:
            - success: Whether prediction setup was successful
            - command: AlphaFold command that would be executed
            - output_dir: Path to output directory
            - metadata: Execution metadata
            - analysis: Input file analysis

    Example:
        >>> result = run_monomer_prediction("input.fasta", "output/")
        >>> print(result['command'])
    """
    # Setup
    input_file = Path(input_file)
    config = {**DEFAULT_CONFIG, **(config or {}), **kwargs}
    paths = get_default_paths()

    # Create sample data if input doesn't exist and enabled
    if not input_file.exists() and config.get("create_sample_if_missing", True):
        input_file.parent.mkdir(parents=True, exist_ok=True)
        create_sample_fasta(input_file, config.get("sample_sequence", "insulin_chain_a"))

    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")

    # Set up output directory
    if output_dir is None:
        output_dir = paths["results_dir"] / "monomer_prediction"
    output_dir = Path(output_dir)
    ensure_directory(output_dir)

    # Analyze input file
    try:
        analysis = analyze_fasta_content(input_file)
        if analysis["is_multimer"]:
            print("Warning: Input contains multiple sequences. Consider using multimer_prediction.py")
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to analyze input file: {e}",
            "input_file": str(input_file)
        }

    # Build AlphaFold command
    try:
        alphafold_cmd = build_alphafold_command(
            fasta_path=input_file,
            output_dir=output_dir,
            alphafold_script=paths["alphafold_script"],
            data_dir=config.get("data_dir"),
            model_preset=config["model_preset"],
            db_preset=config["db_preset"],
            max_template_date=config["max_template_date"]
        )

        # Get resource estimates
        resources = estimate_resources(
            sequence_length=analysis["total_length"],
            is_multimer=analysis["is_multimer"]
        )

        # Demo mode: just show command
        if config.get("demo_mode", True):
            print("=== AlphaFold2 Monomer Prediction Setup ===")
            print(f"Input file: {input_file}")
            print(f"Output directory: {output_dir}")
            print(f"Model preset: {config['model_preset']}")
            print(f"Database preset: {config['db_preset']}")
            print(f"Sequence analysis: {analysis['complex_type']} with {analysis['num_sequences']} sequence(s)")
            print(f"Total length: {analysis['total_length']} amino acids")
            print()
            print("Command that would be executed:")
            print(" ".join(alphafold_cmd))
            print()
            print("Resource estimates:")
            for key, value in resources.items():
                print(f"  {key}: {value}")
            print()
            print("Note: This requires AlphaFold databases to be downloaded (~2.6TB for full, 600GB for reduced)")
            print("Use data_dir parameter to specify database location for actual prediction.")

            success = True
        else:
            # In production mode, you would actually run the command here
            print("Production mode not implemented - would execute AlphaFold command")
            success = False

        return {
            "success": success,
            "command": alphafold_cmd,
            "output_dir": str(output_dir),
            "metadata": {
                "input_file": str(input_file),
                "config": config,
                "analysis": analysis,
                "resources": resources
            }
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to build AlphaFold command: {e}",
            "input_file": str(input_file),
            "config": config
        }

# ==============================================================================
# CLI Interface
# ==============================================================================
def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('--input', '-i', required=True,
                       help='Input FASTA file path')
    parser.add_argument('--output', '-o',
                       help='Output directory path (default: results/monomer_prediction)')
    parser.add_argument('--config', '-c',
                       help='Config file (JSON)')
    parser.add_argument('--model-preset',
                       choices=['monomer', 'monomer_casp14', 'monomer_ptm'],
                       help='Model preset (default: monomer)')
    parser.add_argument('--db-preset',
                       choices=['full_dbs', 'reduced_dbs'],
                       help='Database preset (default: reduced_dbs)')
    parser.add_argument('--data-dir',
                       help='Path to AlphaFold databases')
    parser.add_argument('--max-template-date',
                       help='Maximum template date (YYYY-MM-DD, default: 2022-01-01)')
    parser.add_argument('--create-sample', action='store_true',
                       help='Create sample data and exit')
    parser.add_argument('--production', action='store_true',
                       help='Run in production mode (actually execute AlphaFold)')

    args = parser.parse_args()

    # Handle sample creation
    if args.create_sample:
        sample_path = Path(args.input)
        sample_path.parent.mkdir(parents=True, exist_ok=True)
        create_sample_fasta(sample_path)
        print(f"✅ Sample created: {sample_path}")
        return

    # Load config if provided
    config = DEFAULT_CONFIG.copy()
    if args.config:
        file_config = load_config(args.config)
        config.update(file_config)

    # Override config with command line arguments
    if args.model_preset:
        config["model_preset"] = args.model_preset
    if args.db_preset:
        config["db_preset"] = args.db_preset
    if args.data_dir:
        config["data_dir"] = args.data_dir
    if args.max_template_date:
        config["max_template_date"] = args.max_template_date
    if args.production:
        config["demo_mode"] = False

    # Run prediction
    try:
        result = run_monomer_prediction(
            input_file=args.input,
            output_dir=args.output,
            config=config
        )

        if result["success"]:
            print(f"✅ Setup successful: {result.get('output_dir', 'Completed')}")
        else:
            print(f"❌ Setup failed: {result.get('error', 'Unknown error')}")
            sys.exit(1)

        return result

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()