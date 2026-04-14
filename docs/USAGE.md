# Usage Guide

## Table of Contents
1. [Basic Usage](#basic-usage)
2. [Input Data Preparation](#input-data-preparation)
3. [Running the Pipeline](#running-the-pipeline)
4. [Understanding Outputs](#understanding-outputs)
5. [Advanced Options](#advanced-options)

## Basic Usage

### Minimum Required Command

```bash
nextflow run main.nf \
  --input_dir /path/to/datasets \
  --datasets dataset_name
```

### Common Use Cases

#### 1. Analyze FOXL2 Dataset

```bash
nextflow run main.nf \
  --input_dir /mnt/d/busra-research/doktora/1002/code_works/dataset_prep/datasets \
  --datasets foxl2 \
  --outdir foxl2_results
```

#### 2. Analyze Multiple ClinGen Datasets

```bash
nextflow run main.nf \
  --input_dir /mnt/d/busra-research/doktora/1002/code_works/dataset_prep/datasets \
  --datasets "clingen_28012026,clingen_cancerpredisposition_28012026,clingen_hearing_loss_28012026" \
  --outdir clingen_results
```

#### 3. Analyze with Specific Tools Only

```bash
nextflow run main.nf \
  --input_dir /path/to/datasets \
  --datasets foxl2 \
  --tools "Genebe,Franklin,BIAS,TAPES,InterVar_2018,InterVar_2025" \
  --outdir selected_tools_analysis
```

## Input Data Preparation

### Ground Truth File

The pipeline requires a ground truth file with expert-curated variant classifications.

#### Required Columns

**For FOXL2 datasets (Excel format):**
- `hg38` - Variant coordinates in hg38 (format: `chr-pos-ref-alt`)
- `HGVS` - HGVS notation
- `Classification` - Ground truth classification (Pathogenic, Benign, VUS, etc.)
- `ACMG-AMP classification` - Optional ACMG criteria codes

**For ClinGen/HGMD datasets (TSV format):**
- `Variant_Key` - Unique variant identifier
- `CHROM`, `POS`, `REF`, `ALT` - Variant coordinates
- `Ground_Truth_Classification` - Ground truth classification
- `Ground_Truth_ACMG` - Optional ACMG criteria codes

#### Classification Labels

Use standardized labels:
- `Pathogenic` or `P`
- `Likely_Pathogenic` or `LP`
- `VUS` (Variant of Uncertain Significance)
- `Likely_Benign` or `LB`
- `Benign` or `B`

### Tool Results Directory

### Directory Structure

Your input directory should follow this structure:

```
input_dir/
├── foxl2/
│   └── analysis/
│       └── results/
│           └── foxl2_merged_results.tsv
├── clingen_28012026/
│   └── analysis/
│       └── results/
│           └── clingen_28012026_merged_results.tsv
└── clingen_cancerpredisposition_28012026/
    └── analysis/
        └── results/
            └── clingen_cancerpredisposition_28012026_merged_results.tsv
```

### Required Columns in Merged Results

Your `*_merged_results.tsv` file must contain:

**For Classification Analysis:**
- `Ground_Truth_Classification`: Ground truth classification (P, LP, VUS, LB, B)
- `<Tool>_Classification`: Tool's classification prediction

**For Jaccard Similarity Analysis:**
- `Ground_Truth_ACMG` or `MET_CODES`: Ground truth ACMG criteria
- `<Tool>_ACMG_Criteria`: Tool's ACMG criteria prediction

**Example:**
```
Variant_ID    Ground_Truth_Classification    Genebe_Classification    Ground_Truth_ACMG    Genebe_ACMG_Criteria
chr1:12345    Pathogenic                     Pathogenic               PVS1,PM2,PP3         PVS1,PM2,PP3
chr2:67890    Likely_Benign                  Benign                   BS1,BP4              BS1,BP4,BP7
```

## Running the Pipeline

### Step 1: Prepare Environment

```bash
# Navigate to pipeline directory
cd acmg_analysis_pipeline

# Ensure scripts are executable
chmod +x bin/*.py

# Add bin to PATH (optional)
export PATH=$PATH:$(pwd)/bin
```

### Step 2: Run Pipeline

```bash
nextflow run main.nf \
  --input_dir /path/to/your/datasets \
  --datasets "dataset1,dataset2" \
  --outdir my_analysis_results
```

### Step 3: Monitor Progress

Nextflow will display progress in real-time:

```
N E X T F L O W  ~  version 21.04.0
Launching `main.nf` [peaceful_euler] - revision: abc123

executor >  local (6)
[a1/b2c3d4] process > ACMG_ANALYSIS:CALCULATE_CLASSIFICATION_ACCURACY (foxl2) [100%] 1 of 1 ✔
[e5/f6g7h8] process > ACMG_ANALYSIS:PLOT_CLASSIFICATION_ACCURACY (foxl2)      [100%] 1 of 1 ✔
[i9/j0k1l2] process > ACMG_ANALYSIS:CALCULATE_JACCARD_SIMILARITY (foxl2)      [100%] 1 of 1 ✔
[m3/n4o5p6] process > ACMG_ANALYSIS:PLOT_JACCARD_SIMILARITY (foxl2)           [100%] 1 of 1 ✔
```

## Understanding Outputs

### Output Directory Structure

```
results/
├── foxl2/
│   ├── results/
│   │   ├── classification_accuracy.tsv
│   │   └── jaccard_per_variant.tsv
│   └── figures/
│       ├── classification_accuracy.png
│       ├── pathogenic_benign_recall.png
│       └── jaccard_per_variant.png
├── pipeline_report.html
├── timeline.html
└── trace.txt
```

### Output Files Explained

#### 1. `classification_accuracy.tsv`

Contains accuracy metrics for each tool:

| Tool | Total_Variants | Accuracy | F1_Score | Pathogenic_Recall | Benign_Recall |
|------|----------------|----------|----------|-------------------|---------------|
| Genebe | 288 | 0.892 | 0.885 | 0.950 | 0.820 |
| Franklin | 288 | 0.756 | 0.742 | 0.810 | 0.690 |

#### 2. `jaccard_per_variant.tsv`

Contains Jaccard similarity metrics:

| Tool | Dataset | Avg_Jaccard_Per_Variant | Aggregate_Jaccard | Variants_Analyzed |
|------|---------|-------------------------|-------------------|-------------------|
| Genebe | foxl2 | 0.868 | 0.875 | 288 |
| Franklin | foxl2 | 0.419 | 0.432 | 288 |

#### 3. Figures

- **classification_accuracy.png**: Horizontal bar plot of accuracy per tool
- **pathogenic_benign_recall.png**: Grouped bar plot comparing pathogenic vs benign recall
- **jaccard_per_variant.png**: Horizontal bar plot of Jaccard similarity per tool

## Advanced Options

### Resume a Failed Run

If the pipeline fails or is interrupted:

```bash
nextflow run main.nf -resume \
  --input_dir /path/to/datasets \
  --datasets foxl2
```

### Run with Different Profiles

#### SLURM Cluster

```bash
nextflow run main.nf \
  -profile slurm \
  --input_dir /path/to/datasets \
  --datasets foxl2
```

#### Docker

```bash
nextflow run main.nf \
  -profile docker \
  --input_dir /path/to/datasets \
  --datasets foxl2
```

### Customize Resources

Edit `nextflow.config`:

```groovy
process {
    cpus = 2
    memory = '8 GB'
    time = '2h'
}
```

### Generate Reports

Reports are automatically generated in the output directory:

- `pipeline_report.html`: Detailed execution report
- `timeline.html`: Visual timeline of process execution
- `trace.txt`: Detailed trace of all processes

## Troubleshooting

### Common Issues

**Issue: "Input file not found"**
```
Solution: Check that your input directory structure matches the expected format
```

**Issue: "Permission denied"**
```bash
Solution: Make scripts executable
chmod +x bin/*.py
```

**Issue: "Module not found"**
```bash
Solution: Install Python dependencies
pip install -r requirements.txt
```

### Getting Help

```bash
# Show help message
nextflow run main.nf --help

# Check Nextflow version
nextflow -version

# View pipeline configuration
nextflow config main.nf
```

## Best Practices

1. **Always use absolute paths** for `--input_dir`
2. **Test with one dataset first** before running multiple datasets
3. **Use `-resume`** to save time when re-running
4. **Check logs** in `work/` directory if processes fail
5. **Keep merged results files** in the expected directory structure
