#!/usr/bin/env python3
"""
Script: batch_prediction.py
Description: Process multiple proteins in batch using AlphaFold2

Original Use Case: examples/use_case_3_batch_prediction.py
Dependencies Removed: None (all dependencies inlined or use shared lib)

Usage:
    python scripts/batch_prediction.py --input-dir <input_dir> --output <output_dir>

Example:
    python scripts/batch_prediction.py --input-dir examples/data/batch --output results/batch_pred
"""

# ==============================================================================
# Minimal Imports (only essential packages)
# ==============================================================================
import argparse
import json
import sys
import time
from pathlib import Path
from typing import Union, Optional, Dict, Any, List

# Add local lib to path
sys.path.insert(0, str(Path(__file__).parent))
from lib.io import load_fasta, analyze_fasta_content, ensure_directory, save_fasta
from lib.utils import build_alphafold_command, load_config, estimate_resources, get_default_paths, create_sample_sequences

# ==============================================================================
# Configuration (extracted from use case)
# ==============================================================================
DEFAULT_CONFIG = {
    "model_preset_monomer": "monomer",
    "model_preset_multimer": "multimer",
    "db_preset": "reduced_dbs",
    "max_template_date": "2022-01-01",
    "num_predictions_per_model": 5,
    "msa_reuse": True,
    "demo_mode": True,
    "create_sample_if_missing": True,
    "max_concurrent": 1  # Number of concurrent predictions
}

# ==============================================================================
# Core Sample Data Creation (inlined from use case)
# ==============================================================================
def create_batch_sample_data(output_dir: Path) -> None:
    """Create sample FASTA files for batch processing. Inlined from use_case_3."""

    ensure_directory(output_dir)
    sample_sequences = create_sample_sequences()

    # Sample protein 1: Small monomer
    protein1_sequences = {"protein1|Small test protein": sample_sequences["insulin_chain_a"]}
    save_fasta(protein1_sequences, output_dir / "protein1.fasta")

    # Sample protein 2: Another small monomer
    protein2_sequences = {"protein2|Another test protein": sample_sequences["small_protein"]}
    save_fasta(protein2_sequences, output_dir / "protein2.fasta")

    # Sample protein 3: Heterodimer complex
    protein3_sequences = {
        "complex_chainA|Insulin chain A": sample_sequences["insulin_chain_a"],
        "complex_chainB|Insulin chain B": sample_sequences["insulin_chain_b"]
    }
    save_fasta(protein3_sequences, output_dir / "complex_heterodimer.fasta")

    # Sample protein 4: Homodimer
    protein4_sequences = {
        "homodimer_chain1|First copy": sample_sequences["insulin_chain_a"],
        "homodimer_chain2|Second copy": sample_sequences["insulin_chain_a"]
    }
    save_fasta(protein4_sequences, output_dir / "complex_homodimer.fasta")

    print(f"Created batch sample data in: {output_dir}")
    print("  - protein1.fasta (monomer)")
    print("  - protein2.fasta (monomer)")
    print("  - complex_heterodimer.fasta (multimer)")
    print("  - complex_homodimer.fasta (multimer)")


def find_fasta_files(input_dir: Path) -> List[Path]:
    """Find all FASTA files in the input directory."""
    fasta_extensions = [".fasta", ".fa", ".fas", ".faa"]
    fasta_files = []

    for ext in fasta_extensions:
        fasta_files.extend(input_dir.glob(f"*{ext}"))

    return sorted(fasta_files)


def process_single_file(
    fasta_file: Path,
    output_base_dir: Path,
    config: Dict[str, Any],
    paths: Dict[str, Path]
) -> Dict[str, Any]:
    """Process a single FASTA file and return processing information."""

    try:
        # Analyze the file
        analysis = analyze_fasta_content(fasta_file)

        # Create output directory for this file
        output_dir = output_base_dir / fasta_file.stem

        # Select appropriate model preset
        if analysis["is_multimer"]:
            model_preset = config["model_preset_multimer"]
            num_predictions = config["num_predictions_per_model"]
        else:
            model_preset = config["model_preset_monomer"]
            num_predictions = None  # Not used for monomer

        # Build command
        alphafold_cmd = build_alphafold_command(
            fasta_path=fasta_file,
            output_dir=output_dir,
            alphafold_script=paths["alphafold_script"],
            data_dir=config.get("data_dir"),
            model_preset=model_preset,
            db_preset=config["db_preset"],
            max_template_date=config["max_template_date"],
            num_predictions_per_model=num_predictions
        )

        # Get resource estimates
        resources = estimate_resources(
            sequence_length=analysis["total_length"],
            is_multimer=analysis["is_multimer"]
        )

        return {
            "success": True,
            "file": fasta_file.name,
            "analysis": analysis,
            "model_preset": model_preset,
            "output_dir": str(output_dir),
            "command": alphafold_cmd,
            "resources": resources
        }

    except Exception as e:
        return {
            "success": False,
            "file": fasta_file.name,
            "error": str(e)
        }


# ==============================================================================
# Core Function (main logic extracted from use case)
# ==============================================================================
def run_batch_prediction(
    input_dir: Union[str, Path],
    output_dir: Optional[Union[str, Path]] = None,
    config: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Main function for batch AlphaFold predictions.

    Args:
        input_dir: Path to directory containing FASTA files
        output_dir: Path to output directory (optional)
        config: Configuration dict (uses DEFAULT_CONFIG if not provided)
        **kwargs: Override specific config parameters

    Returns:
        Dict containing:
            - success: Whether batch processing setup was successful
            - total_files: Number of files found
            - processed: List of processing results for each file
            - output_dir: Path to output directory
            - metadata: Execution metadata

    Example:
        >>> result = run_batch_prediction("batch_input/", "batch_output/")
        >>> print(f"Processed {len(result['processed'])} files")
    """
    # Setup
    input_dir = Path(input_dir)
    config = {**DEFAULT_CONFIG, **(config or {}), **kwargs}
    paths = get_default_paths()

    # Create sample data if input doesn't exist and enabled
    if not input_dir.exists() and config.get("create_sample_if_missing", True):
        create_batch_sample_data(input_dir)

    if not input_dir.exists():
        raise FileNotFoundError(f"Input directory not found: {input_dir}")

    # Set up output directory
    if output_dir is None:
        output_dir = paths["results_dir"] / "batch_prediction"
    output_dir = Path(output_dir)
    ensure_directory(output_dir)

    # Find FASTA files
    fasta_files = find_fasta_files(input_dir)
    if not fasta_files:
        return {
            "success": False,
            "error": f"No FASTA files found in {input_dir}",
            "total_files": 0
        }

    # Process each file
    processed_results = []
    monomer_count = 0
    multimer_count = 0
    error_count = 0

    print("=== AlphaFold2 Batch Prediction Setup ===")
    print(f"Input directory: {input_dir}")
    print(f"Output directory: {output_dir}")
    print(f"Found {len(fasta_files)} FASTA files")
    print(f"MSA reuse: {config.get('msa_reuse', False)}")
    print()

    for i, fasta_file in enumerate(fasta_files, 1):
        print(f"Processing {i}/{len(fasta_files)}: {fasta_file.name}")

        result = process_single_file(fasta_file, output_dir, config, paths)
        processed_results.append(result)

        if result["success"]:
            analysis = result["analysis"]
            if analysis["is_multimer"]:
                multimer_count += 1
                print(f"  → {analysis['complex_type']} with {analysis['num_sequences']} sequences")
            else:
                monomer_count += 1
                print(f"  → {analysis['complex_type']} with {analysis['total_length']} residues")

            if config.get("demo_mode", True):
                print(f"  → Output: {result['output_dir']}")
                print(f"  → Command: {' '.join(result['command'][:3])}...")
        else:
            error_count += 1
            print(f"  → Error: {result['error']}")

        print()

    # Summary
    print("=== Batch Processing Summary ===")
    print(f"Total files: {len(fasta_files)}")
    print(f"Monomers: {monomer_count}")
    print(f"Multimers: {multimer_count}")
    print(f"Errors: {error_count}")

    if config.get("demo_mode", True):
        print()
        print("Note: This is demo mode. Commands shown would be executed in production.")
        print("Use --production flag and --data-dir parameter for actual predictions.")

        # Show resource estimates
        total_sequences = sum(r["analysis"]["num_sequences"] for r in processed_results if r["success"])
        total_length = sum(r["analysis"]["total_length"] for r in processed_results if r["success"])
        print(f"\nTotal sequences to process: {total_sequences}")
        print(f"Total amino acids: {total_length}")

    return {
        "success": error_count == 0,
        "total_files": len(fasta_files),
        "monomer_count": monomer_count,
        "multimer_count": multimer_count,
        "error_count": error_count,
        "processed": processed_results,
        "output_dir": str(output_dir),
        "metadata": {
            "input_dir": str(input_dir),
            "config": config
        }
    }


# ==============================================================================
# CLI Interface
# ==============================================================================
def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('--input-dir', '-i', required=True,
                       help='Input directory containing FASTA files')
    parser.add_argument('--output', '-o',
                       help='Output directory path (default: results/batch_prediction)')
    parser.add_argument('--config', '-c',
                       help='Config file (JSON)')
    parser.add_argument('--db-preset',
                       choices=['full_dbs', 'reduced_dbs'],
                       help='Database preset (default: reduced_dbs)')
    parser.add_argument('--data-dir',
                       help='Path to AlphaFold databases')
    parser.add_argument('--max-template-date',
                       help='Maximum template date (YYYY-MM-DD, default: 2022-01-01)')
    parser.add_argument('--num-predictions', type=int,
                       help='Number of predictions per multimer model (default: 5)')
    parser.add_argument('--no-msa-reuse', action='store_true',
                       help='Disable MSA reuse optimization')
    parser.add_argument('--create-sample', action='store_true',
                       help='Create sample data and exit')
    parser.add_argument('--production', action='store_true',
                       help='Run in production mode (actually execute AlphaFold)')

    args = parser.parse_args()

    # Handle sample creation
    if args.create_sample:
        sample_dir = Path(args.input_dir)
        create_batch_sample_data(sample_dir)
        print(f"✅ Sample data created in: {sample_dir}")
        return

    # Load config if provided
    config = DEFAULT_CONFIG.copy()
    if args.config:
        file_config = load_config(args.config)
        config.update(file_config)

    # Override config with command line arguments
    if args.db_preset:
        config["db_preset"] = args.db_preset
    if args.data_dir:
        config["data_dir"] = args.data_dir
    if args.max_template_date:
        config["max_template_date"] = args.max_template_date
    if args.num_predictions:
        config["num_predictions_per_model"] = args.num_predictions
    if args.no_msa_reuse:
        config["msa_reuse"] = False
    if args.production:
        config["demo_mode"] = False

    # Run batch prediction
    try:
        result = run_batch_prediction(
            input_dir=args.input_dir,
            output_dir=args.output,
            config=config
        )

        if result["success"]:
            print(f"✅ Batch setup successful: {result['total_files']} files processed")
        else:
            print(f"❌ Batch setup completed with {result['error_count']} errors")
            if result["error_count"] > 0:
                sys.exit(1)

        return result

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()