# AlphaFold MCP Scripts

Clean, self-contained scripts extracted from use cases for MCP tool wrapping.

## Design Principles

1. **Minimal Dependencies**: Only essential packages imported (argparse, pathlib, json)
2. **Self-Contained**: Functions inlined where possible using shared lib
3. **Configurable**: Parameters in config files, not hardcoded
4. **MCP-Ready**: Each script has a main function ready for MCP wrapping

## Scripts

| Script | Description | Repo Dependent | Config |
|--------|-------------|----------------|--------|
| `monomer_prediction.py` | Predict single protein structure | No | `configs/monomer_config.json` |
| `multimer_prediction.py` | Predict protein complex structure | No | `configs/multimer_config.json` |
| `batch_prediction.py` | Process multiple proteins in batch | No | `configs/batch_config.json` |

## Usage

```bash
# Activate environment (prefer mamba over conda)
mamba activate ./env  # or: conda activate ./env

# Run a script
python scripts/monomer_prediction.py --input examples/data/sample.fasta --output results/output

# Create sample data
python scripts/monomer_prediction.py --input test.fasta --create-sample

# With custom config
python scripts/monomer_prediction.py --input FILE --output DIR --config configs/monomer_config.json
```

## Examples

### Monomer Prediction
```bash
# Create sample data and predict
python scripts/monomer_prediction.py --input protein.fasta --create-sample
python scripts/monomer_prediction.py --input protein.fasta --output results/protein_pred

# With different model preset
python scripts/monomer_prediction.py --input protein.fasta --model-preset monomer_ptm
```

### Multimer Prediction
```bash
# Create heterodimer sample
python scripts/multimer_prediction.py --input complex.fasta --create-sample --complex-type heterodimer

# Predict complex
python scripts/multimer_prediction.py --input complex.fasta --output results/complex_pred
```

### Batch Processing
```bash
# Create batch sample data
python scripts/batch_prediction.py --input-dir batch_data --create-sample

# Process batch
python scripts/batch_prediction.py --input-dir batch_data --output results/batch_pred
```

## Shared Library

Common functions are in `scripts/lib/`:
- `io.py`: FASTA loading/saving, file analysis
- `utils.py`: Command building, configuration, resource estimation

## Configuration Files

Each script can use configuration files in `configs/`:
- `monomer_config.json`: Monomer prediction settings
- `multimer_config.json`: Multimer prediction settings
- `batch_config.json`: Batch processing settings
- `default_config.json`: Default settings for all tools

## For MCP Wrapping (Step 6)

Each script exports a main function that can be wrapped:
```python
from scripts.monomer_prediction import run_monomer_prediction

# In MCP tool:
@mcp.tool()
def predict_monomer_structure(input_file: str, output_dir: str = None):
    return run_monomer_prediction(input_file, output_dir)
```

## Dependencies

### Essential Packages (Python Standard Library)
- `argparse`: Command-line interface
- `pathlib`: Path handling
- `json`: Configuration files
- `sys`: Python path manipulation

### No External Dependencies
All scripts use only Python standard library packages, making them lightweight and portable.

### Repository Dependencies
- Scripts use `repo/alphafold/run_alphafold.py` path but don't import AlphaFold code
- Dependencies are minimal and clearly documented
- Scripts work in demo mode without AlphaFold installation

## Production Setup

For actual AlphaFold predictions:

1. **Download databases**: Use `repo/alphafold/scripts/download_all_data.sh`
2. **Set data directory**: Use `--data-dir /path/to/databases`
3. **Use production mode**: Add `--production` flag
4. **Ensure resources**: 8+ cores, 16+ GB RAM, 600GB+ disk space

## Demo vs Production Mode

**Default (Demo Mode)**:
- Validates inputs and shows command structure
- No actual AlphaFold computation
- Safe for testing and MCP integration

**Production Mode** (`--production` flag):
- Would execute actual AlphaFold commands
- Requires database setup and computational resources
- Use with caution