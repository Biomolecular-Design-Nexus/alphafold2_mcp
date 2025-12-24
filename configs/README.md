# AlphaFold MCP Configuration Files

Configuration files for AlphaFold MCP scripts, extracted from the original use cases.

## Configuration Files

| File | Description | Used By |
|------|-------------|---------|
| `default_config.json` | Common settings for all tools | All scripts |
| `monomer_config.json` | Monomer prediction settings | `monomer_prediction.py` |
| `multimer_config.json` | Multimer prediction settings | `multimer_prediction.py` |
| `batch_config.json` | Batch processing settings | `batch_prediction.py` |

## Usage

### Using Configuration Files

```bash
# Use specific config
python scripts/monomer_prediction.py --input protein.fasta --config configs/monomer_config.json

# Override specific parameters
python scripts/monomer_prediction.py --input protein.fasta --config configs/monomer_config.json --model-preset monomer_ptm
```

### Configuration Structure

All configuration files follow this structure:

```json
{
  "_description": "Description of this config",
  "_source": "Source file it was extracted from",

  "model": {
    "preset": "model_type",
    "preset_options": ["available", "options"]
  },

  "database": {
    "preset": "database_type",
    "max_template_date": "YYYY-MM-DD"
  },

  "execution": {
    "demo_mode": true,
    "create_sample_if_missing": true
  },

  "paths": {
    "data_dir": null,
    "output_dir": "default/output/path"
  }
}
```

## Configuration Options

### Model Presets

**Monomer Models:**
- `monomer`: Standard monomer model
- `monomer_casp14`: CASP14 competition model
- `monomer_ptm`: Model with predicted template modeling

**Multimer Models:**
- `multimer`: AlphaFold-Multimer model for protein complexes

### Database Presets

- `reduced_dbs`: Smaller databases (~600GB) for faster execution
- `full_dbs`: Complete databases (~2.6TB) for highest accuracy

### Execution Options

- `demo_mode`: If true, shows commands without executing
- `create_sample_if_missing`: Auto-create sample data if input missing
- `msa_reuse`: Enable MSA reuse optimization (batch only)

### Sample Data Configuration

Each config includes sample sequence definitions:

```json
"sample_sequences": {
  "insulin_chain_a": {
    "description": "Small test protein (21 residues)",
    "sequence": "GIVEQCCTSICSLYQLENYCN"
  }
}
```

## Customization

### Creating Custom Configurations

1. Copy an existing config file
2. Modify settings as needed
3. Use with `--config` parameter

Example custom config:
```json
{
  "_description": "Custom high-accuracy monomer prediction",

  "model": {
    "preset": "monomer_ptm"
  },

  "database": {
    "preset": "full_dbs",
    "max_template_date": "2023-01-01"
  },

  "execution": {
    "demo_mode": false
  },

  "paths": {
    "data_dir": "/data/alphafold_databases",
    "output_dir": "results/high_accuracy"
  }
}
```

### Configuration Inheritance

1. **Default config** provides base settings
2. **Script-specific config** overrides defaults
3. **Command-line arguments** override config files

Priority order: CLI args > config file > defaults

## Validation

All configurations are validated when loaded:
- Required fields must be present
- Model presets must be valid options
- Paths must be accessible (when specified)
- Dates must be in YYYY-MM-DD format