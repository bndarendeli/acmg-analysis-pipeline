#!/usr/bin/bash

# Example pipeline runs

# Set paths
INPUT_DIR="/mnt/d/busra-research/doktora/1002/code_works/dataset_prep/datasets"
OUTPUT_DIR="results"
CONFIG_FILE="conf/datasets_config.json"

echo "================================================================================"
echo "ACMG Analysis Pipeline - Examples"
echo "================================================================================"

# Example 1: Full pipeline - Parse FOXL2 from raw outputs
echo ""
echo "Example 1: Full end-to-end pipeline for FOXL2"
echo "  Parse raw tool outputs → Merge → Analyze (Accuracy + Jaccard + VUS)"
nextflow run main.nf \
  --input_dir ${INPUT_DIR} \
  --datasets foxl2 \
  --config_file ${CONFIG_FILE} \
  --outdir ${OUTPUT_DIR}/foxl2_full

# Example 2: Skip parsing - Use existing merged results
echo ""
echo "Example 2: Skip parsing, use existing merged results"
nextflow run main.nf \
  --input_dir ${INPUT_DIR} \
  --datasets foxl2 \
  --skip_parsing \
  --outdir ${OUTPUT_DIR}/foxl2_analysis

# Example 3: Multiple datasets with parsing
echo ""
echo "Example 3: Multiple datasets (if configured)"
nextflow run main.nf \
  --input_dir ${INPUT_DIR} \
  --datasets "foxl2,clingen_28012026" \
  --config_file ${CONFIG_FILE} \
  --outdir ${OUTPUT_DIR}/multi_dataset

# Example 4: Custom tools selection
echo ""
echo "Example 4: Analyze with specific tools only"
nextflow run main.nf \
  --input_dir ${INPUT_DIR} \
  --datasets foxl2 \
  --tools "Genebe,Franklin,BIAS,TAPES" \
  --skip_parsing \
  --outdir ${OUTPUT_DIR}/selected_tools

echo ""
echo "================================================================================"
echo "Examples completed! Check ${OUTPUT_DIR}/ for results"
echo "================================================================================"
