# AlphaFold2 MCP

> AlphaFold2 protein structure prediction via Model Context Protocol (MCP)

## Table of Contents
- [Overview](#overview)
- [Installation](#installation)
- [Local Usage (Scripts)](#local-usage-scripts)
- [MCP Server Installation](#mcp-server-installation)
- [Using with Claude Code](#using-with-claude-code)
- [Using with Gemini CLI](#using-with-gemini-cli)
- [Available Tools](#available-tools)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)

## Overview

This MCP provides access to AlphaFold2 protein structure prediction capabilities through both local scripts and MCP server tools. It supports single protein folding, protein complex prediction, and batch processing of multiple proteins.

### Features
- **Monomer Structure Prediction**: Predict 3D structure of single proteins using AlphaFold2
- **Multimer Complex Prediction**: Predict protein complexes using AlphaFold-Multimer
- **Batch Processing**: Process multiple proteins efficiently in batch mode
- **Job Management**: Submit long-running jobs and track their progress
- **Analysis Tools**: Quick FASTA file analysis and recommendations

### Directory Structure
```
./
├── README.md               # This file
├── env/                    # Conda environment
├── src/
│   └── server.py           # MCP server
├── scripts/
│   ├── monomer_prediction.py   # Single protein structure prediction
│   ├── multimer_prediction.py  # Protein complex prediction
│   ├── batch_prediction.py     # Multiple proteins processing
│   └── lib/                    # Shared utilities
├── examples/
│   └── data/                   # Demo data
├── configs/                    # Configuration files
└── repo/                       # Original AlphaFold repository
```

---

## Installation

### Quick Setup (Recommended)

Run the automated setup script:

```bash
cd alphafold2_mcp
bash quick_setup.sh
```

The script will create the conda environment, install all dependencies, and display the Claude Code configuration. See `quick_setup.sh --help` for options like `--skip-env` or `--skip-repo`.

### Prerequisites
- Conda or Mamba (mamba recommended for faster installation)
- Python 3.10+
- 16-32GB RAM (64GB+ for large complexes)
- AlphaFold databases (~600GB reduced, ~2.6TB full)

### Manual Installation (Alternative)

If you prefer manual installation or need to customize the setup, follow the information in `reports/step3_environment.md`:

```bash
# Navigate to the MCP directory
cd /home/xux/Desktop/ProteinMCP/ProteinMCP/tool-mcps/alphafold2_mcp

# Create conda environment (use mamba if available)
mamba create -p ./env python=3.10 -y
# or: conda create -p ./env python=3.10 -y

# Activate environment
mamba activate ./env
# or: conda activate ./env

# Install Dependencies
pip install -r requirements.txt

# Install MCP dependencies
pip install fastmcp loguru --ignore-installed
```

---

## Local Usage (Scripts)

You can use the scripts directly without MCP for local processing.

### Available Scripts

| Script | Description | Example |
|--------|-------------|---------|
| `scripts/monomer_prediction.py` | Single protein structure prediction | See below |
| `scripts/multimer_prediction.py` | Protein complex prediction | See below |
| `scripts/batch_prediction.py` | Multiple proteins processing | See below |

### Script Examples

#### Monomer Prediction

```bash
# Activate environment
mamba activate ./env

# Run script
python scripts/monomer_prediction.py \
  --input examples/data/monomer.fasta \
  --output results/monomer_pred \
  --config configs/monomer_config.json
```

**Parameters:**
- `--input, -i`: Path to FASTA file with single protein sequence (required)
- `--output, -o`: Output directory for results (default: results/)
- `--config, -c`: Configuration file path (optional)
- `--model-preset`: AlphaFold model preset (monomer, monomer_casp14, monomer_ptm)
- `--db-preset`: Database preset (full_dbs, reduced_dbs)

#### Multimer Prediction

```bash
python scripts/multimer_prediction.py \
  --input examples/data/complex.fasta \
  --output results/complex_pred \
  --num-predictions 5
```

**Parameters:**
- `--input, -i`: Path to FASTA file with multiple protein sequences (required)
- `--output, -o`: Output directory for results (default: results/)
- `--config, -c`: Configuration file path (optional)
- `--num-predictions`: Number of prediction attempts (default: 5)

#### Batch Prediction

```bash
python scripts/batch_prediction.py \
  --input-dir examples/data/batch \
  --output results/batch_pred \
  --config configs/batch_config.json
```

**Parameters:**
- `--input-dir`: Directory containing FASTA files (required)
- `--output, -o`: Output directory for results (default: results/)
- `--config, -c`: Configuration file path (optional)

---

## MCP Server Installation

### Option 1: Using fastmcp (Recommended)

```bash
# Install MCP server for Claude Code
fastmcp install src/server.py --name alphafold2
```

### Option 2: Manual Installation for Claude Code

```bash
# Add MCP server to Claude Code
claude mcp add alphafold2 -- $(pwd)/env/bin/python $(pwd)/src/server.py

# Verify installation
claude mcp list
```

### Option 3: Configure in settings.json

Add to `~/.claude/settings.json`:

```json
{
  "mcpServers": {
    "alphafold2": {
      "command": "/home/xux/Desktop/ProteinMCP/ProteinMCP/tool-mcps/alphafold2_mcp/env/bin/python",
      "args": ["/home/xux/Desktop/ProteinMCP/ProteinMCP/tool-mcps/alphafold2_mcp/src/server.py"]
    }
  }
}
```

---

## Using with Claude Code

After installing the MCP server, you can use it directly in Claude Code.

### Quick Start

```bash
# Start Claude Code
claude
```

### Example Prompts

#### Tool Discovery
```
What tools are available from alphafold2?
```

#### Basic Usage
```
Use submit_monomer_prediction with input file @examples/data/monomer.fasta
```

#### With Configuration
```
Run submit_multimer_prediction on @examples/data/complex.fasta with 3 predictions per model
```

#### Long-Running Tasks (Submit API)
```
Submit monomer prediction for @examples/data/monomer.fasta
Then check the job status
```

#### Batch Processing
```
Process these files in batch:
- @examples/data/batch/
```

### Using @ References

In Claude Code, use `@` to reference files and directories:

| Reference | Description |
|-----------|-------------|
| `@examples/data/monomer.fasta` | Reference a specific file |
| `@configs/monomer_config.json` | Reference a config file |
| `@results/` | Reference output directory |

---

## Using with Gemini CLI

### Configuration

Add to `~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "alphafold2": {
      "command": "/home/xux/Desktop/ProteinMCP/ProteinMCP/tool-mcps/alphafold2_mcp/env/bin/python",
      "args": ["/home/xux/Desktop/ProteinMCP/ProteinMCP/tool-mcps/alphafold2_mcp/src/server.py"]
    }
  }
}
```

### Example Prompts

```bash
# Start Gemini CLI
gemini

# Example prompts (same as Claude Code)
> What tools are available?
> Use submit_monomer_prediction with file examples/data/monomer.fasta
```

---

## Available Tools

### Quick Operations (Sync API)

These tools return results immediately (< 10 minutes):

| Tool | Description | Parameters |
|------|-------------|------------|
| `analyze_fasta_file` | Analyze FASTA content and get recommendations | `input_file` |
| `create_sample_data` | Generate sample test files | `output_dir`, `data_type` |
| `get_server_info` | Get server capabilities and usage info | None |

### Long-Running Tasks (Submit API)

These tools return a job_id for tracking (> 10 minutes):

| Tool | Description | Parameters |
|------|-------------|------------|
| `submit_monomer_prediction` | Single protein structure prediction | `input_file`, `model_preset`, `db_preset`, ... |
| `submit_multimer_prediction` | Protein complex prediction | `input_file`, `num_predictions_per_model`, ... |
| `submit_batch_prediction` | Multiple proteins processing | `input_dir`, `db_preset`, ... |

### Job Management Tools

| Tool | Description |
|------|-------------|
| `get_job_status` | Check job progress |
| `get_job_result` | Get results when completed |
| `get_job_log` | View execution logs |
| `cancel_job` | Cancel running job |
| `list_jobs` | List all jobs |

---

## Examples

### Example 1: Single Protein Structure Prediction

**Goal:** Predict the 3D structure of insulin chain A

**Using Script:**
```bash
python scripts/monomer_prediction.py \
  --input examples/data/monomer.fasta \
  --output results/insulin_a/
```

**Using MCP (in Claude Code):**
```
Use submit_monomer_prediction to process @examples/data/monomer.fasta and save results to results/insulin_a/
```

**Expected Output:**
- Ranked PDB structure files (ranked_0.pdb, etc.)
- Confidence scores and features
- Performance metrics

### Example 2: Protein Complex Prediction

**Goal:** Predict the structure of insulin heterodimer complex

**Using Script:**
```bash
python scripts/multimer_prediction.py \
  --input examples/data/complex.fasta \
  --config configs/multimer_config.json
```

**Using MCP (in Claude Code):**
```
Run submit_multimer_prediction on @examples/data/complex.fasta with config @configs/multimer_config.json
```

**Expected Output:**
- Complex structure files with inter-chain confidence scores
- Ranking information and analysis

### Example 3: Batch Processing

**Goal:** Process multiple files at once

**Using Script:**
```bash
python scripts/batch_prediction.py \
  --input-dir examples/data/batch \
  --output results/batch_pred/
```

**Using MCP (in Claude Code):**
```
Submit batch processing for all files in @examples/data/batch/
```

**Expected Output:**
- Organized results for each protein
- Batch processing summary and statistics

---

## Demo Data

The `examples/data/` directory contains sample data for testing:

| File | Description | Use With |
|------|-------------|----------|
| `monomer.fasta` | Single protein sequence (Insulin chain A, 21 AA) | `submit_monomer_prediction` |
| `complex.fasta` | Protein heterodimer (Insulin A+B chains, 51 AA) | `submit_multimer_prediction` |
| `homodimer.fasta` | Homodimer complex example | `submit_multimer_prediction` |
| `batch/` | Directory with multiple FASTA files | `submit_batch_prediction` |
| `example.json` | Server configuration example | Reference |

---

## Configuration Files

The `configs/` directory contains configuration templates:

| Config | Description | Parameters |
|--------|-------------|------------|
| `default_config.json` | Common settings for all scripts | model, database, execution, paths |
| `monomer_config.json` | Monomer prediction settings | model_preset, db_preset, max_template_date |
| `multimer_config.json` | Multimer prediction settings | num_predictions, model_preset, db_preset |
| `batch_config.json` | Batch processing settings | batch_size, parallel_jobs, resource_limits |

### Config Example

```json
{
  "model_preset": "monomer",
  "db_preset": "reduced_dbs",
  "max_template_date": "2022-01-01",
  "use_gpu": true
}
```

---

## Troubleshooting

### Environment Issues

**Problem:** Environment not found
```bash
# Recreate environment
mamba create -p ./env python=3.10 -y
mamba activate ./env
pip install -r requirements.txt
```

**Problem:** Import errors
```bash
# Verify installation
python -c "from src.server import mcp"
```

### MCP Issues

**Problem:** Server not found in Claude Code
```bash
# Check MCP registration
claude mcp list

# Re-add if needed
claude mcp remove alphafold2
claude mcp add alphafold2 -- $(pwd)/env/bin/python $(pwd)/src/server.py
```

**Problem:** Tools not working
```bash
# Test server directly
python -c "
from src.server import mcp
print(list(mcp.list_tools().keys()))
"
```

### Job Issues

**Problem:** Job stuck in pending
```bash
# Check job directory
ls -la jobs/

# View job log
cat jobs/<job_id>/job.log
```

**Problem:** Job failed
```
Use get_job_log with job_id "<job_id>" and tail 100 to see error details
```

### Database Issues

**Problem:** Missing AlphaFold databases
- Download AlphaFold databases (600GB-2.6TB)
- Use `reduced_dbs` preset for faster testing
- Set `data_dir` parameter to database location

**Problem:** Out of memory
- Use smaller proteins for testing
- Increase system RAM or use reduced databases
- Set memory limits in batch processing config

---

## Development

### Running Tests

```bash
# Activate environment
mamba activate ./env

# Test server startup
python src/server.py --help

# Test individual scripts
python scripts/monomer_prediction.py --help
```

### Starting Dev Server

```bash
# Run MCP server in dev mode
fastmcp dev src/server.py
```

### Environment Requirements

- **Minimum RAM**: 16GB for small proteins
- **Recommended RAM**: 32GB+ for large proteins and complexes
- **Storage**: Significant space for databases and results
- **GPU**: Recommended for faster inference (optional)

---

## Performance Considerations

### Execution Time Estimates
- **Small monomer** (100 residues): 30+ minutes
- **Medium monomer** (300 residues): 1-3 hours
- **Large monomer** (1000+ residues): 6-24 hours
- **Multimer complex**: 2-10x longer than individual chains

### Resource Optimization
- Use `reduced_dbs` for faster MSA generation
- Enable GPU acceleration when available
- Batch processing for efficiency with related sequences
- Monitor job progress with `get_job_log`

---

## License

Based on [DeepMind AlphaFold](https://github.com/deepmind/alphafold) v2.3.2

## Credits

- **AlphaFold2**: DeepMind Technologies
- **MCP Implementation**: Built with FastMCP framework
- **Job Management**: Custom async job queue system

