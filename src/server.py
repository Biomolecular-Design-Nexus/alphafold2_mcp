"""MCP Server for AlphaFold2

Provides both synchronous and asynchronous (submit) APIs for AlphaFold2 structure predictions.
"""

from fastmcp import FastMCP
from pathlib import Path
from typing import Optional, List
import sys

# Setup paths
SCRIPT_DIR = Path(__file__).parent.resolve()
MCP_ROOT = SCRIPT_DIR.parent
SCRIPTS_DIR = MCP_ROOT / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))
sys.path.insert(0, str(SCRIPTS_DIR))

from jobs.manager import job_manager
from loguru import logger

# Create MCP server
mcp = FastMCP("alphafold2")

# ==============================================================================
# Job Management Tools (for async operations)
# ==============================================================================

@mcp.tool()
def get_job_status(job_id: str) -> dict:
    """
    Get the status of a submitted job.

    Args:
        job_id: The job ID returned from a submit_* function

    Returns:
        Dictionary with job status, timestamps, and any errors
    """
    return job_manager.get_job_status(job_id)


@mcp.tool()
def get_job_result(job_id: str) -> dict:
    """
    Get the results of a completed job.

    Args:
        job_id: The job ID of a completed job

    Returns:
        Dictionary with the job results or error if not completed
    """
    return job_manager.get_job_result(job_id)


@mcp.tool()
def get_job_log(job_id: str, tail: int = 50) -> dict:
    """
    Get log output from a running or completed job.

    Args:
        job_id: The job ID to get logs for
        tail: Number of lines from end (default: 50, use 0 for all)

    Returns:
        Dictionary with log lines and total line count
    """
    return job_manager.get_job_log(job_id, tail)


@mcp.tool()
def cancel_job(job_id: str) -> dict:
    """
    Cancel a running job.

    Args:
        job_id: The job ID to cancel

    Returns:
        Success or error message
    """
    return job_manager.cancel_job(job_id)


@mcp.tool()
def list_jobs(status: Optional[str] = None) -> dict:
    """
    List all submitted jobs.

    Args:
        status: Filter by status (pending, running, completed, failed, cancelled)

    Returns:
        List of jobs with their status
    """
    return job_manager.list_jobs(status)


# ==============================================================================
# AlphaFold2 Structure Prediction Tools (Submit API for long-running operations)
# ==============================================================================

@mcp.tool()
def submit_monomer_prediction(
    input_file: str,
    model_preset: str = "monomer",
    db_preset: str = "reduced_dbs",
    max_template_date: str = "2022-01-01",
    data_dir: Optional[str] = None,
    output_dir: Optional[str] = None,
    job_name: Optional[str] = None
) -> dict:
    """
    Submit a monomer structure prediction for background processing.

    Predicts the 3D structure of a single protein sequence using AlphaFold2.
    This operation may take 30+ minutes depending on sequence length and system resources.

    Args:
        input_file: Path to FASTA file containing a single protein sequence
        model_preset: AlphaFold model preset (monomer, monomer_casp14, monomer_ptm)
        db_preset: Database preset (full_dbs, reduced_dbs)
        max_template_date: Maximum template date (YYYY-MM-DD format)
        data_dir: Path to AlphaFold databases (required for production)
        output_dir: Directory to save outputs
        job_name: Optional name for the job (for easier tracking)

    Returns:
        Dictionary with job_id for tracking. Use:
        - get_job_status(job_id) to check progress
        - get_job_result(job_id) to get results when completed
        - get_job_log(job_id) to see execution logs

    Example:
        Submit insulin chain A prediction:
        result = submit_monomer_prediction("examples/data/insulin_a.fasta")
        job_id = result["job_id"]
    """
    script_path = str(SCRIPTS_DIR / "monomer_prediction.py")

    return job_manager.submit_job(
        script_path=script_path,
        args={
            "input": input_file,
            "model_preset": model_preset,
            "db_preset": db_preset,
            "max_template_date": max_template_date,
            "data_dir": data_dir,
            "output": output_dir
        },
        job_name=job_name or f"monomer_{Path(input_file).stem}"
    )


@mcp.tool()
def submit_multimer_prediction(
    input_file: str,
    model_preset: str = "multimer",
    db_preset: str = "reduced_dbs",
    num_predictions_per_model: int = 5,
    max_template_date: str = "2022-01-01",
    data_dir: Optional[str] = None,
    output_dir: Optional[str] = None,
    job_name: Optional[str] = None
) -> dict:
    """
    Submit a multimer structure prediction for background processing.

    Predicts the 3D structure of a protein complex using AlphaFold-Multimer.
    This operation may take 60+ minutes depending on complex size and system resources.

    Args:
        input_file: Path to FASTA file containing multiple protein sequences
        model_preset: AlphaFold model preset (currently only "multimer" supported)
        db_preset: Database preset (full_dbs, reduced_dbs)
        num_predictions_per_model: Number of prediction attempts (default: 5)
        max_template_date: Maximum template date (YYYY-MM-DD format)
        data_dir: Path to AlphaFold databases (required for production)
        output_dir: Directory to save outputs
        job_name: Optional name for the job (for easier tracking)

    Returns:
        Dictionary with job_id for tracking. Use:
        - get_job_status(job_id) to check progress
        - get_job_result(job_id) to get results when completed
        - get_job_log(job_id) to see execution logs

    Example:
        Submit insulin heterodimer prediction:
        result = submit_multimer_prediction("examples/data/insulin_complex.fasta")
        job_id = result["job_id"]
    """
    script_path = str(SCRIPTS_DIR / "multimer_prediction.py")

    return job_manager.submit_job(
        script_path=script_path,
        args={
            "input": input_file,
            "model_preset": model_preset,
            "db_preset": db_preset,
            "num_predictions": num_predictions_per_model,
            "max_template_date": max_template_date,
            "data_dir": data_dir,
            "output": output_dir
        },
        job_name=job_name or f"multimer_{Path(input_file).stem}"
    )


@mcp.tool()
def submit_batch_prediction(
    input_dir: str,
    db_preset: str = "reduced_dbs",
    max_template_date: str = "2022-01-01",
    num_predictions_per_model: int = 5,
    data_dir: Optional[str] = None,
    output_dir: Optional[str] = None,
    job_name: Optional[str] = None
) -> dict:
    """
    Submit batch processing for multiple proteins in a directory.

    Processes all FASTA files in a directory, automatically choosing monomer
    or multimer mode based on the number of sequences in each file.
    This operation may take 2+ hours depending on the number and size of proteins.

    Args:
        input_dir: Path to directory containing FASTA files (.fasta, .fa, .fas, .faa)
        db_preset: Database preset (full_dbs, reduced_dbs)
        max_template_date: Maximum template date (YYYY-MM-DD format)
        num_predictions_per_model: Number of predictions per multimer model
        data_dir: Path to AlphaFold databases (required for production)
        output_dir: Directory to save outputs
        job_name: Optional name for the batch job

    Returns:
        Dictionary with job_id for tracking the batch job. Use:
        - get_job_status(job_id) to check progress
        - get_job_result(job_id) to get results when completed
        - get_job_log(job_id) to see execution logs

    Example:
        Submit batch processing for a directory of proteins:
        result = submit_batch_prediction("examples/data/batch/")
        job_id = result["job_id"]
    """
    script_path = str(SCRIPTS_DIR / "batch_prediction.py")

    return job_manager.submit_job(
        script_path=script_path,
        args={
            "input_dir": input_dir,
            "db_preset": db_preset,
            "max_template_date": max_template_date,
            "num_predictions": num_predictions_per_model,
            "data_dir": data_dir,
            "output": output_dir
        },
        job_name=job_name or f"batch_{Path(input_dir).name}"
    )


# ==============================================================================
# Convenience and Analysis Tools (Synchronous API for fast operations)
# ==============================================================================

@mcp.tool()
def analyze_fasta_file(input_file: str) -> dict:
    """
    Analyze a FASTA file to understand its contents and structure.

    Quick analysis to determine if the file contains monomer or multimer sequences,
    sequence lengths, and provides recommendations for which prediction tool to use.

    Args:
        input_file: Path to FASTA file to analyze

    Returns:
        Dictionary with analysis results including:
        - complex_type: "monomer" or "multimer" or "batch"
        - num_sequences: Number of sequences in file
        - total_length: Total amino acid count
        - recommendations: Suggested prediction method

    Example:
        Analyze a protein file:
        result = analyze_fasta_file("examples/data/protein.fasta")
        print(f"Type: {result['complex_type']}")
    """
    try:
        from lib.io import analyze_fasta_content

        analysis = analyze_fasta_content(input_file)

        # Add recommendations
        if analysis["is_multimer"]:
            recommendation = "Use submit_multimer_prediction() for this file"
            estimated_time = "60+ minutes"
        else:
            recommendation = "Use submit_monomer_prediction() for this file"
            estimated_time = "30+ minutes"

        return {
            "status": "success",
            "analysis": analysis,
            "recommendation": recommendation,
            "estimated_time": estimated_time,
            "note": "Times are estimates and depend on sequence length and system resources"
        }

    except FileNotFoundError:
        return {"status": "error", "error": f"File not found: {input_file}"}
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        return {"status": "error", "error": str(e)}


@mcp.tool()
def create_sample_data(
    output_dir: str,
    data_type: str = "all"
) -> dict:
    """
    Create sample FASTA files for testing AlphaFold predictions.

    Generates example protein sequences that can be used to test the prediction tools
    without needing your own data.

    Args:
        output_dir: Directory to create sample files in
        data_type: Type of sample data to create:
            - "monomer": Single protein sequence
            - "multimer": Multi-protein complex
            - "batch": Directory with multiple files
            - "all": Create all sample types (default)

    Returns:
        Dictionary with paths to created files and usage examples

    Example:
        Create test data for trying the tools:
        result = create_sample_data("examples/test_data/")
        # Then use the created files with prediction tools
    """
    try:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        from lib.utils import create_sample_sequences
        from lib.io import save_fasta

        sequences = create_sample_sequences()
        created_files = []

        if data_type in ["monomer", "all"]:
            # Create monomer sample
            monomer_file = output_path / "sample_monomer.fasta"
            monomer_data = {
                "insulin_chain_a|Sample insulin A chain": sequences["insulin_chain_a"]
            }
            save_fasta(monomer_data, monomer_file)
            created_files.append(str(monomer_file))

        if data_type in ["multimer", "all"]:
            # Create multimer sample
            multimer_file = output_path / "sample_multimer.fasta"
            multimer_data = {
                "insulin_chain_a|Insulin A chain": sequences["insulin_chain_a"],
                "insulin_chain_b|Insulin B chain": sequences["insulin_chain_b"]
            }
            save_fasta(multimer_data, multimer_file)
            created_files.append(str(multimer_file))

        if data_type in ["batch", "all"]:
            # Create batch directory
            batch_dir = output_path / "batch_samples"
            batch_dir.mkdir(exist_ok=True)

            # Protein 1: monomer
            p1_file = batch_dir / "protein1.fasta"
            save_fasta({"protein1|Small protein": sequences["small_protein"]}, p1_file)
            created_files.append(str(p1_file))

            # Protein 2: another monomer
            p2_file = batch_dir / "protein2.fasta"
            save_fasta({"protein2|Insulin chain A": sequences["insulin_chain_a"]}, p2_file)
            created_files.append(str(p2_file))

            # Complex: multimer
            complex_file = batch_dir / "complex.fasta"
            complex_data = {
                "complex_a|Insulin A": sequences["insulin_chain_a"],
                "complex_b|Insulin B": sequences["insulin_chain_b"]
            }
            save_fasta(complex_data, complex_file)
            created_files.append(str(complex_file))

        # Create usage examples
        examples = []
        if "sample_monomer.fasta" in str(created_files):
            examples.append(f"submit_monomer_prediction('{output_path}/sample_monomer.fasta')")
        if "sample_multimer.fasta" in str(created_files):
            examples.append(f"submit_multimer_prediction('{output_path}/sample_multimer.fasta')")
        if "batch_samples" in str(created_files):
            examples.append(f"submit_batch_prediction('{output_path}/batch_samples/')")

        return {
            "status": "success",
            "created_files": created_files,
            "total_files": len(created_files),
            "usage_examples": examples,
            "note": "Use these files to test AlphaFold prediction tools"
        }

    except Exception as e:
        logger.error(f"Sample creation failed: {e}")
        return {"status": "error", "error": str(e)}


@mcp.tool()
def get_server_info() -> dict:
    """
    Get information about the AlphaFold2 MCP server and available tools.

    Returns:
        Dictionary with server capabilities, tool descriptions, and usage examples
    """
    return {
        "server_name": "AlphaFold2 MCP Server",
        "version": "1.0.0",
        "description": "MCP server for AlphaFold2 structure predictions",
        "available_tools": {
            "prediction_tools": [
                "submit_monomer_prediction",
                "submit_multimer_prediction",
                "submit_batch_prediction"
            ],
            "job_management": [
                "get_job_status",
                "get_job_result",
                "get_job_log",
                "cancel_job",
                "list_jobs"
            ],
            "utilities": [
                "analyze_fasta_file",
                "create_sample_data",
                "get_server_info"
            ]
        },
        "workflow_examples": {
            "single_protein": [
                "1. create_sample_data('examples/', 'monomer')",
                "2. submit_monomer_prediction('examples/sample_monomer.fasta')",
                "3. get_job_status(job_id)",
                "4. get_job_result(job_id) when completed"
            ],
            "protein_complex": [
                "1. submit_multimer_prediction('complex.fasta')",
                "2. Monitor with get_job_status(job_id)",
                "3. Get results with get_job_result(job_id)"
            ],
            "batch_processing": [
                "1. submit_batch_prediction('proteins_dir/')",
                "2. Track progress with get_job_log(job_id)",
                "3. Get all results with get_job_result(job_id)"
            ]
        },
        "requirements": {
            "databases": "AlphaFold databases required for production runs (~600GB-2.6TB)",
            "compute": "GPU recommended for faster predictions",
            "time": "30min-2hrs+ depending on sequence length and complexity"
        }
    }


# ==============================================================================
# Entry Point
# ==============================================================================

if __name__ == "__main__":
    mcp.run()