# ACMG Analysis Pipeline - End-to-End

Complete pipeline from raw tool outputs to final analysis results.

## 🚀 Quick Start

### Full Pipeline (Parse → Merge → Analyze)

```bash
nextflow run main_endtoend.nf \
  --input_dir /path/to/datasets \
  --datasets foxl2 \
  --config_file conf/datasets_config.json
```

### Skip Parsing (Use Existing Merged Results)

```bash
nextflow run main_endtoend.nf \
  --input_dir /path/to/datasets \
  --datasets foxl2 \
  --skip_parsing
```

## 📋 Pipeline Workflow

```
Raw Tool Outputs
      ↓
[1. PARSE] - Parse each tool's output format
      ↓
[2. MERGE] - Merge with ground truth
      ↓
Merged Results TSV
      ↓
[3. ANALYZE] - Three comprehensive analyses:
   • Classification Accuracy
   • Jaccard Similarity (Per-Variant)
   • VUS Misclassification
      ↓
Results + Publication-Ready Figures
```

## 📁 Input Directory Structure

### For Full Pipeline (with Parsing)

```
input_dir/
└── foxl2/
    ├── FOXL2_dataset.xlsx          # Ground truth
    └── results_fix/                # Raw tool outputs
        ├── foxl2_hg38_genebe.vcf
        ├── foxl2_hg38_intervar_20180118.txt
        ├── foxl2_hg38_intervar_20250721.txt
        ├── foxl2_hg38_BIAS.tsv
        ├── foxl2_hg38_CharGer_local_annotated_VEPv97.tsv
        ├── foxl2_hg38_CharGer_online.tsv
        ├── foxl2_hg38_DiabloACMG.tsv
        ├── foxl2_hg38_exomiser.tsv
        ├── foxl2_hg38_tapes.csv
        ├── foxl2_hg19_franklin.csv
        ├── foxl2_hg38_autogvp.tsv
        └── foxl2_hg19_viphl.tsv
```

### For Skip Parsing Mode

```
input_dir/
└── foxl2/
    └── analysis/
        └── results/
            └── foxl2_merged_results.tsv  # Pre-existing merged results
```

## ⚙️ Configuration File

Create `conf/datasets_config.json`:

```json
{
  "foxl2": {
    "ground_truth": "FOXL2_dataset.xlsx",
    "results_dir": "results_fix",
    "tool_files": {
      "Genebe": "foxl2_hg38_genebe.vcf",
      "InterVar_2018": "foxl2_hg38_intervar_20180118.txt",
      "InterVar_2025": "foxl2_hg38_intervar_20250721.txt",
      "BIAS": "foxl2_hg38_BIAS.tsv",
      "CharGer_Local": "foxl2_hg38_CharGer_local_annotated_VEPv97.tsv",
      "CharGer_Online": "foxl2_hg38_CharGer_online.tsv",
      "DiabloACMG": "foxl2_hg38_DiabloACMG.tsv",
      "Exomiser": "foxl2_hg38_exomiser.tsv",
      "TAPES": "foxl2_hg38_tapes.csv",
      "Franklin": "foxl2_hg19_franklin.csv",
      "AutoGVP": "foxl2_hg38_autogvp.tsv",
      "VIP-HL": "foxl2_hg19_viphl.tsv"
    }
  }
}
```

## 📊 Output Structure

```
results/
└── foxl2/
    ├── parsed/
    │   └── foxl2_merged_results.tsv           # Parsed and merged data
    ├── results/
    │   ├── classification_accuracy.tsv
    │   ├── jaccard_per_variant.tsv
    │   └── vus_misclassification_metrics.tsv  # VUS analysis metrics
    └── figures/
        ├── classification_accuracy.png
        ├── pathogenic_benign_recall.png
        ├── jaccard_per_variant.png
        ├── vus_overall_rate.png               # VUS over-assignment rate
        ├── vus_by_category.png                # VUS by pathogenic/benign
        └── correct_vs_vus.png                 # Correct vs VUS stacked bar
```

## 🔧 Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `--input_dir` | Yes | - | Input directory containing datasets |
| `--datasets` | Yes | - | Comma-separated dataset names |
| `--outdir` | No | `results` | Output directory |
| `--tools` | No | All tools | Comma-separated tool names |
| `--skip_parsing` | No | `false` | Skip parsing, use existing merged results |
| `--config_file` | No | - | JSON config file with dataset settings |

## 📝 Examples

### Example 1: Full Pipeline for FOXL2

```bash
nextflow run main.nf \
  --input_dir /mnt/d/busra-research/doktora/1002/code_works/dataset_prep/datasets \
  --datasets foxl2 \
  --config_file conf/datasets_config.json \
  --outdir foxl2_results
```

### Example 2: Multiple Datasets

```bash
nextflow run main.nf \
  --input_dir /path/to/datasets \
  --datasets "foxl2,clingen_28012026" \
  --config_file conf/datasets_config.json
```

### Example 3: Custom Tools

```bash
nextflow run main.nf \
  --input_dir /path/to/datasets \
  --datasets foxl2 \
  --tools "Genebe,Franklin,BIAS,TAPES" \
  --skip_parsing
```

### Example 4: Resume Failed Run

```bash
nextflow run main.nf -resume \
  --input_dir /path/to/datasets \
  --datasets foxl2 \
  --config_file conf/datasets_config.json
```

## 🔍 Supported Tools

The pipeline supports parsing for:
- Genebe (VCF)
- Franklin (CSV)
- InterVar (2018 & 2025 versions)
- BIAS
- CharGer (Local & Online)
- DiabloACMG
- Exomiser
- TAPES
- AutoGVP
- VIP-HL

## 🐛 Troubleshooting

### Parser Not Found

**Error:** `Parser not found for tool: ToolName`

**Solution:** Ensure the tool is supported and the parser exists in `bin/parsers/`

### Ground Truth Not Found

**Error:** `Ground truth not found for dataset: dataset_name`

**Solution:** Check that the ground truth file exists and is named correctly in the config

### Tool File Not Found

**Warning:** `Warning: filename not found, skipping ToolName`

**Solution:** Verify the tool output file exists in the results directory and matches the config

## 📚 Additional Documentation

- `README.md` - Main pipeline documentation (analysis-only mode)
- `docs/USAGE.md` - Detailed usage guide
- `example_endtoend_run.sh` - Example run scripts

## � Analysis Modules

The pipeline includes three comprehensive analysis modules:

1. **Classification Accuracy**
   - Overall accuracy and F1-score
   - Pathogenic and benign recall rates
   - Tool comparison visualizations

2. **Jaccard Similarity (Per-Variant)**
   - Compares complete ACMG criteria sets per variant
   - Measures intersection over union
   - Identifies tools with best criteria matching

3. **VUS Misclassification** ⭐ NEW
   - Analyzes VUS over-assignment to non-VUS variants
   - Separate metrics for pathogenic and benign categories
   - Identifies tools that incorrectly assign VUS
