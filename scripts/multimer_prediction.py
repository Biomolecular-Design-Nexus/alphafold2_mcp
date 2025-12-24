#!/usr/bin/env python3
"""
Script: multimer_prediction.py
Description: Predict protein complex structure using AlphaFold-Multimer

Original Use Case: examples/use_case_2_multimer_prediction.py
Dependencies Removed: None (all dependencies inlined or use shared lib)

Usage:
    python scripts/multimer_prediction.py --input <input_file> --output <output_dir>

Example:
    python scripts/multimer_prediction.py --input examples/data/complex.fasta --output results/multimer_pred
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
    "model_preset": "multimer",
    "db_preset": "reduced_dbs",
    "max_template_date": "2022-01-01",
    "num_predictions_per_model": 5,
    "demo_mode": True,
    "create_sample_if_missing": True,
    "sample_complex_type": "heterodimer"
}

# ==============================================================================
# Core Sample Data Creation (inlined from use case)
# ==============================================================================
def create_sample_multimer_fasta(output_path: Path, complex_type: str = 'heterodimer') -> None:
    """Create a sample multimer FASTA file for testing. Inlined from use_case_2."""

    sample_sequences = create_sample_sequences()

    if complex_type == 'heterodimer':
        # Example: Insulin heterodimer (chain A and chain B)
        sequences = {
            "insulin_chain_a|Insulin A chain": sample_sequences["insulin_chain_a"],
            "insulin_chain_b|Insulin B chain": sample_sequences["insulin_chain_b"]
        }

    elif complex_type == 'homodimer':
        # Example: Same sequence repeated twice
        sequences = {
            "protein_copy_1|First copy of homodimer": sample_sequences["insulin_chain_a"],
            "protein_copy_2|Second copy of homodimer": sample_sequences["insulin_chain_a"]
        }

    elif complex_type == 'trimer':
        # Example: Three-protein complex
        sequences = {
            "protein_a|Protein A in trimer": sample_sequences["insulin_chain_a"],
            "protein_b|Protein B in trimer": sample_sequences["insulin_chain_b"],
            "protein_c|Protein C in trimer": sample_sequences["small_protein"]
        }

    else:
        # Default to heterodimer
        sequences = {
            "protein_1|First protein": sample_sequences["insulin_chain_a"],
            "protein_2|Second protein": sample_sequences["insulin_chain_b"]
        }

    save_fasta(sequences, output_path)
    print(f"Created sample multimer FASTA file ({complex_type}): {output_path}")


# ==============================================================================
# Core Function (main logic extracted from use case)
# ==============================================================================
def run_multimer_prediction(
    input_file: Union[str, Path],
    output_dir: Optional[Union[str, Path]] = None,
    config: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Main function for AlphaFold-Multimer complex structure prediction.

    Args:
        input_file: Path to input FASTA file containing multiple sequences
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
        >>> result = run_multimer_prediction("complex.fasta", "output/")
        >>> print(result['command'])
    """
    # Setup
    input_file = Path(input_file)
    config = {**DEFAULT_CONFIG, **(config or {}), **kwargs}
    paths = get_default_paths()

    # Create sample data if input doesn't exist and enabled
    if not input_file.exists() and config.get("create_sample_if_missing", True):
        input_file.parent.mkdir(parents=True, exist_ok=True)
        create_sample_multimer_fasta(
            input_file,
            config.get("sample_complex_type", "heterodimer")
        )

    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")

    # Set up output directory
    if output_dir is None:
        output_dir = paths["results_dir"] / "multimer_prediction"
    output_dir = Path(output_dir)
    ensure_directory(output_dir)

    # Analyze input file
    try:
        analysis = analyze_fasta_content(input_file)
        if not analysis["is_multimer"]:
            print("Warning: Input contains only one sequence. Consider using monomer_prediction.py")
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
            max_template_date=config["max_template_date"],
            num_predictions_per_model=config["num_predictions_per_model"]
        )

        # Get resource estimates
        resources = estimate_resources(
            sequence_length=analysis["total_length"],
            is_multimer=analysis["is_multimer"]
        )

        # Demo mode: just show command
        if config.get("demo_mode", True):
            print("=== AlphaFold-Multimer Complex Prediction Setup ===")
            print(f"Input file: {input_file}")
            print(f"Output directory: {output_dir}")
            print(f"Model preset: {config['model_preset']}")
            print(f"Database preset: {config['db_preset']}")
            print(f"Predictions per model: {config['num_predictions_per_model']}")
            print()
            print("Complex analysis:")
            print(f"  Type: {analysis['complex_type']}")
            print(f"  Number of sequences: {analysis['num_sequences']}")
            print(f"  Total length: {analysis['total_length']} amino acids")
            print("  Sequences:")
            for header, length in analysis['sequences']:
                print(f"    - {header}: {length} residues")
            print()
            print("Command that would be executed:")
            print(" ".join(alphafold_cmd))
            print()
            print("Resource estimates:")
            for key, value in resources.items():
                print(f"  {key}: {value}")
            print()
            print("Note: Multimer predictions require additional databases and significantly more compute time")
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
                       help='Input FASTA file with multiple protein sequences')
    parser.add_argument('--output', '-o',
                       help='Output directory path (default: results/multimer_prediction)')
    parser.add_argument('--config', '-c',
                       help='Config file (JSON)')
    parser.add_argument('--model-preset',
                       choices=['multimer'],
                       help='Model preset (default: multimer)')
    parser.add_argument('--db-preset',
                       choices=['full_dbs', 'reduced_dbs'],
                       help='Database preset (default: reduced_dbs)')
    parser.add_argument('--data-dir',
                       help='Path to AlphaFold databases')
    parser.add_argument('--max-template-date',
                       help='Maximum template date (YYYY-MM-DD, default: 2022-01-01)')
    parser.add_argument('--num-predictions', type=int,
                       help='Number of predictions per model (default: 5)')
    parser.add_argument('--complex-type',
                       choices=['heterodimer', 'homodimer', 'trimer'],
                       help='Type of complex for sample creation')
    parser.add_argument('--create-sample', action='store_true',
                       help='Create sample data and exit')
    parser.add_argument('--production', action='store_true',
                       help='Run in production mode (actually execute AlphaFold)')

    args = parser.parse_args()

    # Handle sample creation
    if args.create_sample:
        sample_path = Path(args.input)
        sample_path.parent.mkdir(parents=True, exist_ok=True)
        complex_type = args.complex_type or 'heterodimer'
        create_sample_multimer_fasta(sample_path, complex_type)
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
    if args.num_predictions:
        config["num_predictions_per_model"] = args.num_predictions
    if args.complex_type:
        config["sample_complex_type"] = args.complex_type
    if args.production:
        config["demo_mode"] = False

    # Run prediction
    try:
        result = run_multimer_prediction(
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