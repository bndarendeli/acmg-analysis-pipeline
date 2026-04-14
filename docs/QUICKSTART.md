# Quick Start Guide - Running the Pipeline from Zero

This guide walks you through running the ACMG Analysis Pipeline from scratch.

---

## 📋 Prerequisites

Before starting, ensure you have:

1. **Nextflow** installed (version 20.0+)
   ```bash
   curl -s https://get.nextflow.io | bash
   sudo mv nextflow /usr/local/bin/
   ```

2. **Python 3.8+** with required packages
   ```bash
   pip install -r requirements.txt
   ```

3. **Your data:**
   - Raw tool output files (VCF, TSV, CSV from ACMG tools)
   - Ground truth file OR annotated VCF to create ground truth

---

## 🚀 Step-by-Step Tutorial

### **Step 1: Clone/Download the Pipeline**

```bash
# If from GitHub
git clone https://github.com/yourusername/acmg-analysis-pipeline.git
cd acmg-analysis-pipeline

# Or if you already have it
cd /path/to/acmg_analysis_pipeline
```

---

### **Step 2: Prepare Your Data Directory**

Organize your data in this structure:

```
my_datasets/
└── my_dataset_name/
    ├── ground_truth.xlsx          # Your ground truth (or create in Step 3)
    └── tool_results/              # Raw tool outputs
        ├── dataset_genebe.vcf
        ├── dataset_franklin.csv
        ├── dataset_BIAS.tsv
        ├── dataset_intervar.txt
        └── ... (other tool outputs)
```

**Example for ClinGen dataset:**
```
datasets/
└── clingen_28012026/
    ├── clingen_ground_truth.xlsx
    └── tool_results/
        ├── clingen_genebe.vcf
        ├── clingen_franklin.csv
        ├── clingen_BIAS.tsv
        └── ...
```

---

### **Step 3: Create Ground Truth (if needed)**

#### **Option A: From Annotated VCF**

If you have a VCF file with ClinVar/HGMD annotations:

```bash
python bin/prepare_ground_truth.py \
  --vcf datasets/clingen_28012026/clingen_annotated.vcf \
  --dataset clingen_28012026 \
  --output-dir datasets/clingen_28012026 \
  --format excel \
  --create-notvus
```

This creates:
- `clingen_28012026_ground_truth.xlsx`
- `clingen_28012026_notvus_ground_truth.xlsx`

#### **Option B: Manual Creation**

Create an Excel file with these columns:
- `Chr`, `Pos`, `Ref`, `Alt` - Variant coordinates
- `Variant_Key` - Format: `chr-pos-ref-alt`
- `CLASSIFICATION` - Pathogenic, Benign, VUS, etc.
- `MET_CODES` - ACMG criteria (optional)
- `Dataset` - Dataset name

---

### **Step 4: Create Configuration File**

Create `conf/datasets_config.json`:

```json
{
  "clingen_28012026": {
    "ground_truth": "clingen_ground_truth.xlsx",
    "results_dir": "tool_results",
    "tool_files": {
      "Genebe": "clingen_genebe.vcf",
      "Franklin": "clingen_franklin.csv",
      "BIAS": "clingen_BIAS.tsv",
      "InterVar_2018": "clingen_intervar_20180118.txt",
      "InterVar_2025": "clingen_intervar_20250721.txt",
      "TAPES": "clingen_tapes.csv"
    }
  }
}
```

**Important:** Adjust file names to match your actual tool output files.

---

### **Step 5: Run the Pipeline**

#### **Full Pipeline (Parse → Merge → Analyze)**

```bash
nextflow run main.nf \
  --input_dir /path/to/datasets \
  --datasets clingen_28012026 \
  --config_file conf/datasets_config.json \
  --outdir results
```

#### **If You Already Have Merged Results**

```bash
nextflow run main.nf \
  --input_dir /path/to/datasets \
  --datasets clingen_28012026 \
  --skip_parsing \
  --outdir results
```

---

### **Step 6: Monitor Progress**

Nextflow will show progress:

```
N E X T F L O W  ~  version 21.04.0
Launching `main.nf` [clever_euler] - revision: abc123

executor >  local (12)
[xx/xxxxxx] process > ACMG_ANALYSIS:PARSE_AND_MERGE (clingen_28012026)        [100%] 1 of 1 ✔
[xx/xxxxxx] process > ACMG_ANALYSIS:CALCULATE_CLASSIFICATION_ACCURACY (...)   [100%] 1 of 1 ✔
[xx/xxxxxx] process > ACMG_ANALYSIS:PLOT_CLASSIFICATION_ACCURACY (...)        [100%] 1 of 1 ✔
[xx/xxxxxx] process > ACMG_ANALYSIS:CALCULATE_JACCARD_SIMILARITY (...)        [100%] 1 of 1 ✔
[xx/xxxxxx] process > ACMG_ANALYSIS:PLOT_JACCARD_SIMILARITY (...)             [100%] 1 of 1 ✔
[xx/xxxxxx] process > ACMG_ANALYSIS:ANALYZE_VUS_MISCLASSIFICATION (...)       [100%] 1 of 1 ✔

Completed at: 14-Apr-2026 19:45:23
Duration    : 5m 32s
CPU hours   : 0.2
Succeeded   : 12
```

---

### **Step 7: Check Results**

Your results will be in the output directory:

```
results/
└── clingen_28012026/
    ├── parsed/
    │   └── clingen_28012026_merged_results.tsv
    ├── results/
    │   ├── classification_accuracy.tsv
    │   ├── jaccard_per_variant.tsv
    │   └── vus_misclassification_metrics.tsv
    └── figures/
        ├── classification_accuracy.png
        ├── pathogenic_benign_recall.png
        ├── jaccard_per_variant.png
        ├── vus_overall_rate.png
        ├── vus_by_category.png
        └── correct_vs_vus.png
```

**Total output:**
- 3 TSV files with metrics
- 6 publication-ready figures

---

## 📊 Understanding the Results

### **1. Classification Accuracy (`classification_accuracy.tsv`)**

Shows how well each tool classifies variants:

| Tool | Accuracy | F1_Score | Pathogenic_Recall | Benign_Recall |
|------|----------|----------|-------------------|---------------|
| Genebe | 0.85 | 0.82 | 0.88 | 0.81 |
| Franklin | 0.83 | 0.80 | 0.85 | 0.80 |

### **2. Jaccard Similarity (`jaccard_per_variant.tsv`)**

Measures how well tools match ACMG criteria:

| Tool | Mean_Jaccard | Median_Jaccard | Std_Jaccard |
|------|--------------|----------------|-------------|
| Genebe | 0.65 | 0.70 | 0.25 |
| Franklin | 0.62 | 0.68 | 0.27 |

### **3. VUS Misclassification (`vus_misclassification_metrics.tsv`)**

Shows how often tools incorrectly assign VUS:

| Tool | VUS_Assignment_Rate | Pathogenic_VUS_Rate | Benign_VUS_Rate |
|------|---------------------|---------------------|-----------------|
| Genebe | 0.15 | 0.12 | 0.18 |
| Franklin | 0.20 | 0.18 | 0.22 |

---

## 🔧 Advanced Usage

### **Auto-Discover All Datasets**

```bash
# Process all datasets in input directory
nextflow run main.nf \
  --input_dir /path/to/datasets \
  --config_file conf/datasets_config.json \
  --outdir results
```

### **Multiple Specific Datasets**

```bash
nextflow run main.nf \
  --input_dir /path/to/datasets \
  --datasets "clingen_28012026,foxl2,hgmd_clinvar_cancer" \
  --config_file conf/datasets_config.json \
  --outdir results
```

### **Specific Tools Only**

```bash
nextflow run main.nf \
  --input_dir /path/to/datasets \
  --datasets clingen_28012026 \
  --tools "Genebe,Franklin,BIAS,TAPES" \
  --outdir results
```

### **Resume Failed Run**

```bash
nextflow run main.nf -resume \
  --input_dir /path/to/datasets \
  --datasets clingen_28012026 \
  --config_file conf/datasets_config.json
```

---

## 🐛 Troubleshooting

### **Error: "Ground truth not found"**

**Solution:** Check that:
1. Ground truth file exists in dataset directory
2. File name in config matches actual file name
3. Path in `--input_dir` is correct

### **Error: "Parser not found for tool: ToolName"**

**Solution:** 
1. Check tool name spelling in config
2. Verify tool is supported (see README for list)
3. Ensure parser exists in `bin/parsers/`

### **Error: "Tool file not found"**

**Solution:**
1. Verify tool output file exists in results directory
2. Check file name in config matches actual file
3. Ensure file path is relative to dataset directory

### **Pipeline Hangs or Fails**

**Solution:**
1. Check Nextflow work directory: `work/`
2. Look at `.command.log` files for error messages
3. Run with `-resume` to continue from last successful step

---

## 📚 Next Steps

1. **Explore Results:** Open figures in `results/{dataset}/figures/`
2. **Analyze Metrics:** Load TSV files into Excel/Python for deeper analysis
3. **Compare Datasets:** Create master ground truth for cross-dataset comparison
4. **Customize:** Modify scripts in `bin/` for custom analyses

---

## 💡 Tips

- **Start small:** Test with one dataset first
- **Check data:** Verify ground truth and tool outputs before running
- **Use resume:** Always use `-resume` if pipeline fails
- **Monitor resources:** Check CPU/memory usage for large datasets
- **Backup results:** Copy results directory before re-running

---

## 📞 Getting Help

- Check `README.md` for detailed documentation
- See `docs/USAGE.md` for advanced usage
- Review example scripts in `example_run.sh`
- Check GitHub issues for common problems

---

**You're ready to run the pipeline! 🚀**
