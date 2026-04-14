# ACMG Analysis Pipeline

Complete end-to-end pipeline for ACMG variant classification tool evaluation.

## 🚀 Quick Start

### Full Pipeline (Parse → Merge → Analyze)

```bash
nextflow run main.nf \
  --input_dir /path/to/datasets \
  --datasets foxl2 \
  --config_file conf/datasets_config.json
```

### Skip Parsing (Use Existing Merged Results)

```bash
nextflow run main.nf \
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

### Required Inputs

Each dataset requires:
1. **Ground truth file** - Variant classifications (Excel or TSV)
2. **Tool results directory** - Raw output files from ACMG classification tools

### Example: FOXL2 Dataset

```
input_dir/
└── foxl2/
    ├── FOXL2_dataset.xlsx          # Ground truth
    └── results_fix/                # Tool results directory
        ├── foxl2_hg38_genebe.vcf
        ├── foxl2_hg38_intervar_20180118.txt
        ├── foxl2_hg38_BIAS.tsv
        ├── foxl2_hg38_DiabloACMG.tsv
        ├── foxl2_hg38_exomiser.tsv
        └── ... (other tool outputs)
```

### Example: ClinGen Dataset

```
input_dir/
└── clingen_28012026/
    ├── ground_truth.tsv            # Ground truth
    └── tool_results/               # Tool results directory
        ├── clingen_genebe.vcf
        ├── clingen_intervar.txt
        ├── clingen_BIAS.tsv
        └── ... (other tool outputs)
```

### Example: HGMD-ClinVar Dataset

```
input_dir/
└── hgmd_clinvar_cancer/
    ├── ground_truth.tsv            # Ground truth
    └── tool_results/               # Tool results directory
        ├── hgmd_clinvar_genebe.vcf
        ├── hgmd_clinvar_franklin.csv
        └── ... (other tool outputs)
```

### For Skip Parsing Mode

If you already have merged results:

```
input_dir/
└── <dataset>/
    └── analysis/
        └── results/
            └── <dataset>_merged_results.tsv
```

---

## 📝 Ground Truth Preparation

The pipeline can prepare ground truth files from annotated VCF files, or you can provide pre-prepared ground truth files.

### Option 1: Automated Ground Truth Preparation (Recommended)

The pipeline includes a ground truth preparation module that extracts variant classifications from VCF files annotated with ClinVar/HGMD data.

**What it does:**
- Extracts variant coordinates, classifications, and ACMG codes from VCF
- Standardizes classification labels
- Creates both complete and NotVUS (non-VUS) versions
- Outputs Excel or TSV format

**Usage:**
```bash
# Prepare ground truth from VCF
python bin/prepare_ground_truth.py \
  --vcf /path/to/annotated_variants.vcf \
  --dataset clingen_28012026 \
  --output-dir ground_truth \
  --format excel \
  --create-notvus
```

**VCF Requirements:**
Your VCF file should contain these INFO fields:
- `CLASSIFICATION` - Variant classification (Pathogenic, Benign, VUS, etc.)
- `MET_CODES` - ACMG criteria codes that are met
- `NOT_MET_CODES` - ACMG criteria codes that are not met
- `GENE` - Gene symbol

**Output:**
- `{dataset}_ground_truth.xlsx` - All variants
- `{dataset}_notvus_ground_truth.xlsx` - Non-VUS variants only (for VUS misclassification analysis)

### Creating Master Ground Truth (Multiple Datasets)

Combine multiple individual dataset ground truths into a single master ground truth for cross-dataset analysis:

```bash
# Combine multiple ground truth files
python bin/create_master_ground_truth.py \
  --input-files \
    ground_truth/clingen_28012026_ground_truth.xlsx \
    ground_truth/foxl2_ground_truth.xlsx \
    ground_truth/hgmd_clinvar_cancer_ground_truth.xlsx \
  --output ground_truth/master_ground_truth.xlsx \
  --create-notvus
```

**What it does:**
- Combines multiple dataset ground truths into one file
- Preserves dataset labels for cross-dataset comparison
- Creates both complete and NotVUS master versions
- Useful for analyzing tool performance across multiple datasets

**Output:**
- `master_ground_truth.xlsx` - All variants from all datasets
- `master_notvus_ground_truth.xlsx` - Non-VUS variants from all datasets

### Option 2: Manual Ground Truth Preparation

If you prefer to create ground truth files manually, follow these format requirements:

### FOXL2 Dataset Format (Excel)

For FOXL2 datasets, use an Excel file (`.xlsx`) with the following columns:

| Column | Required | Description | Example |
|--------|----------|-------------|---------|
| `hg38` | Yes | Variant coordinates (hg38) | `chr3-138946704-CG-C` |
| `hg19` | Optional | Variant coordinates (hg19) | `chr3-138945020-CG-C` |
| `HGVS` | Yes | HGVS notation | `NM_023067.4:c.402dupC` |
| `Classification` | Yes | Ground truth classification | `Pathogenic`, `Benign`, `VUS`, etc. |
| `ACMG-AMP classification` | Optional | ACMG criteria codes | `PVS1,PM2,PP3` |

**Example FOXL2 ground truth:**
```
hg38                        hg19                        HGVS                    Classification  ACMG-AMP classification
chr3-138946704-CG-C        chr3-138945020-CG-C         NM_023067.4:c.402dupC   Pathogenic      PVS1,PM2,PP3
chr3-138946729-C-T         chr3-138945045-C-T          NM_023067.4:c.427C>T    Pathogenic      PS3,PM1,PM2,PP3
chr3-138946750-G-A         chr3-138945066-G-A          NM_023067.4:c.448G>A    Benign          BA1
```

### ClinGen/HGMD-ClinVar Format (TSV)

For ClinGen and HGMD-ClinVar datasets, use a TSV file with these columns:

| Column | Required | Description | Example |
|--------|----------|-------------|---------|
| `Variant_Key` | Yes | Variant identifier | `1-12345-A-T` |
| `CHROM` | Yes | Chromosome | `1` |
| `POS` | Yes | Position | `12345` |
| `REF` | Yes | Reference allele | `A` |
| `ALT` | Yes | Alternate allele | `T` |
| `Ground_Truth_Classification` | Yes | Classification | `Pathogenic`, `Benign`, etc. |
| `Ground_Truth_ACMG` | Optional | ACMG criteria | `PS1,PM2,PP3` |

**Example ClinGen ground truth (TSV):**
```tsv
Variant_Key    CHROM  POS     REF  ALT  Ground_Truth_Classification  Ground_Truth_ACMG
1-12345-A-T    1      12345   A    T    Pathogenic                   PS1,PM2,PP3
2-67890-G-C    2      67890   G    C    Benign                       BA1
3-11111-C-T    3      11111   C    T    VUS                          PM2
```

### Creating Your Ground Truth File

**Step 1: Collect Variant Information**
- Variant coordinates (chromosome, position, ref, alt)
- HGVS notation (recommended)
- Expert-curated classifications

**Step 2: Format According to Dataset Type**

For **FOXL2-like datasets** (Excel):
```python
import pandas as pd

data = {
    'hg38': ['chr3-138946704-CG-C', 'chr3-138946729-C-T'],
    'hg19': ['chr3-138945020-CG-C', 'chr3-138945045-C-T'],
    'HGVS': ['NM_023067.4:c.402dupC', 'NM_023067.4:c.427C>T'],
    'Classification': ['Pathogenic', 'Pathogenic'],
    'ACMG-AMP classification': ['PVS1,PM2,PP3', 'PS3,PM1,PM2,PP3']
}

df = pd.DataFrame(data)
df.to_excel('FOXL2_dataset.xlsx', index=False)
```

For **ClinGen/HGMD-ClinVar datasets** (TSV):
```python
import pandas as pd

data = {
    'Variant_Key': ['1-12345-A-T', '2-67890-G-C'],
    'CHROM': ['1', '2'],
    'POS': [12345, 67890],
    'REF': ['A', 'G'],
    'ALT': ['T', 'C'],
    'Ground_Truth_Classification': ['Pathogenic', 'Benign'],
    'Ground_Truth_ACMG': ['PS1,PM2,PP3', 'BA1']
}

df = pd.DataFrame(data)
df.to_csv('ground_truth.tsv', sep='\t', index=False)
```

**Step 3: Validate Your Ground Truth**
- Ensure all required columns are present
- Check variant coordinates are correctly formatted
- Verify classifications use standard terms: `Pathogenic`, `Likely_Pathogenic`, `VUS`, `Likely_Benign`, `Benign`
- Remove duplicate variants

### Classification Standards

Use these standardized classification labels:

| Label | Abbreviation | Description |
|-------|--------------|-------------|
| `Pathogenic` | P | Pathogenic variant |
| `Likely_Pathogenic` | LP | Likely pathogenic variant |
| `VUS` | VUS | Variant of uncertain significance |
| `Likely_Benign` | LB | Likely benign variant |
| `Benign` | B | Benign variant |

---

## ⚙️ Configuration File

Create `conf/datasets_config.json` to specify dataset-specific settings:

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
  },
  "clingen_28012026": {
    "ground_truth": "ground_truth.tsv",
    "results_dir": "tool_results",
    "tool_files": {
      "Genebe": "clingen_genebe.vcf",
      "Franklin": "clingen_franklin.csv",
      "BIAS": "clingen_BIAS.tsv",
      "InterVar_2018": "clingen_intervar_20180118.txt",
      "InterVar_2025": "clingen_intervar_20250721.txt"
    }
  },
  "hgmd_clinvar_cancer": {
    "ground_truth": "ground_truth.tsv",
    "results_dir": "tool_results",
    "tool_files": {
      "Genebe": "hgmd_clinvar_genebe.vcf",
      "Franklin": "hgmd_clinvar_franklin.csv",
      "BIAS": "hgmd_clinvar_BIAS.tsv"
    }
  }
}
```

**Note:** Adjust file names and paths according to your actual dataset structure.

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

### Example 1: Prepare Ground Truth from VCF

```bash
# Prepare ground truth for ClinGen dataset
python bin/prepare_ground_truth.py \
  --vcf datasets/clingen_28012026/clingen_28012026_hg38.vcf \
  --dataset clingen_28012026 \
  --output-dir ground_truth \
  --format excel \
  --create-notvus

# This creates:
# - clingen_28012026_ground_truth.xlsx (all variants)
# - clingen_28012026_notvus_ground_truth.xlsx (non-VUS only)
```

### Example 2: Create Master Ground Truth

```bash
# Combine multiple datasets into master ground truth
python bin/create_master_ground_truth.py \
  --input-files \
    ground_truth/clingen_28012026_ground_truth.xlsx \
    ground_truth/clingen_cancerpredisposition_28012026_ground_truth.xlsx \
    ground_truth/clingen_hearing_loss_28012026_ground_truth.xlsx \
    ground_truth/hgmd_clinvar_cancer_ground_truth.xlsx \
    ground_truth/hgmd_clinvar_hl_ground_truth.xlsx \
  --output ground_truth/master_ground_truth_5datasets.xlsx \
  --create-notvus

# This creates:
# - master_ground_truth_5datasets.xlsx (all variants from 5 datasets)
# - master_notvus_ground_truth_5datasets.xlsx (non-VUS only)
```

### Example 3: Analyze FOXL2 Dataset

```bash
nextflow run main.nf \
  --input_dir /path/to/datasets \
  --datasets foxl2 \
  --config_file conf/datasets_config.json \
  --outdir results/foxl2
```

### Example 4: Analyze ClinGen Dataset

```bash
nextflow run main.nf \
  --input_dir /path/to/datasets \
  --datasets clingen_28012026 \
  --config_file conf/datasets_config.json \
  --outdir results/clingen
```

### Example 5: Analyze HGMD-ClinVar Dataset

```bash
nextflow run main.nf \
  --input_dir /path/to/datasets \
  --datasets hgmd_clinvar_cancer \
  --config_file conf/datasets_config.json \
  --outdir results/hgmd_clinvar
```

### Example 6: Multiple Datasets

```bash
nextflow run main.nf \
  --input_dir /path/to/datasets \
  --datasets "foxl2,clingen_28012026,hgmd_clinvar_cancer" \
  --config_file conf/datasets_config.json \
  --outdir results/all_datasets
```

### Example 7: Skip Parsing (Use Existing Merged Results)

```bash
nextflow run main.nf \
  --input_dir /path/to/datasets \
  --datasets foxl2 \
  --skip_parsing \
  --outdir results/foxl2_analysis_only
```

### Example 8: Custom Tools Selection

```bash
nextflow run main.nf \
  --input_dir /path/to/datasets \
  --datasets foxl2 \
  --tools "Genebe,Franklin,BIAS,TAPES" \
  --skip_parsing
```

### Example 9: Resume Failed Run

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

- `README.md` - This file (main pipeline documentation)
- `docs/USAGE.md` - Detailed usage guide
- `example_run.sh` - Example run scripts
- `conf/datasets_config.json` - Dataset configuration examples

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
