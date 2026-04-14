#!/usr/bin/env nextflow

/*
 * ACMG Analysis Pipeline - End-to-End
 * 
 * Complete pipeline: Raw Tool Outputs → Parse → Merge → Analyze
 * Includes classification accuracy and Jaccard similarity analysis
 */

nextflow.enable.dsl=2

// Import workflows
include { ACMG_ANALYSIS } from './workflows/acmg_analysis'

// Default parameters
params.input_dir = null
params.outdir = 'results'
params.datasets = null
params.tools = 'Genebe,Franklin,BIAS,TAPES,InterVar_2018,InterVar_2025,DiabloACMG,Exomiser,AutoGVP,VIP-HL,CharGer_Local,CharGer_Online'
params.skip_parsing = false  // Set to true to use pre-existing merged results
params.config_file = null    // Optional: JSON config file with dataset-specific settings

// Help message
def helpMessage() {
    log.info"""
    ================================================================
    ACMG Analysis Pipeline - End-to-End
    ================================================================
    
    Usage:
      # Full pipeline (parse → merge → analyze)
      nextflow run main_endtoend.nf --input_dir <path> --datasets <names> --config_file <config.json>
      
      # Skip parsing (use existing merged results)
      nextflow run main_endtoend.nf --input_dir <path> --datasets <names> --skip_parsing
    
    Required arguments:
      --input_dir DIR        Input directory containing datasets
      --datasets NAMES       Comma-separated dataset names
    
    Optional arguments:
      --outdir DIR           Output directory (default: results)
      --tools NAMES          Comma-separated tool names
      --skip_parsing         Skip parsing, use existing merged results
      --config_file FILE     JSON config file with dataset settings
      --help                 Show this help message
    
    Dataset Directory Structure (for parsing):
      input_dir/
        <dataset>/
          FOXL2_dataset.xlsx          # Ground truth (FOXL2)
          ground_truth.tsv            # Ground truth (ClinGen)
          results_fix/                # Tool output files
            foxl2_hg38_genebe.vcf
            foxl2_hg38_intervar_*.txt
            ...
    
    Config File Format (JSON):
      {
        "foxl2": {
          "ground_truth": "FOXL2_dataset.xlsx",
          "results_dir": "results_fix",
          "tool_files": {
            "Genebe": "foxl2_hg38_genebe.vcf",
            "InterVar_2018": "foxl2_hg38_intervar_20180118.txt",
            ...
          }
        }
      }
    
    Examples:
      # Full end-to-end pipeline
      nextflow run main_endtoend.nf \\
        --input_dir /path/to/datasets \\
        --datasets foxl2 \\
        --config_file datasets_config.json
      
      # Use existing merged results
      nextflow run main_endtoend.nf \\
        --input_dir /path/to/datasets \\
        --datasets foxl2 \\
        --skip_parsing
    
    Output:
      results/
        <dataset>/
          parsed/
            <dataset>_merged_results.tsv
          results/
            classification_accuracy.tsv
            jaccard_per_variant.tsv
          figures/
            classification_accuracy.png
            jaccard_per_variant.png
    
    ================================================================
    """.stripIndent()
}

// Show help
if (params.help) {
    helpMessage()
    exit 0
}

// Validate parameters
if (!params.input_dir) {
    log.error "ERROR: --input_dir is required"
    helpMessage()
    exit 1
}

if (!params.datasets) {
    log.error "ERROR: --datasets is required"
    helpMessage()
    exit 1
}

// Load config file if provided
def dataset_configs = [:]
if (params.config_file) {
    def config_file = file(params.config_file)
    if (config_file.exists()) {
        dataset_configs = new groovy.json.JsonSlurper().parse(config_file)
        log.info "Loaded dataset configurations from: ${params.config_file}"
    } else {
        log.warn "Config file not found: ${params.config_file}, using defaults"
    }
}

// Main workflow
workflow {
    // Parse datasets
    dataset_list = params.datasets.tokenize(',').collect { it.trim() }
    tools_list = params.tools.tokenize(',').collect { it.trim() }
    
    log.info """
    ================================================================
    ACMG Analysis Pipeline
    ================================================================
    Input directory : ${params.input_dir}
    Output directory: ${params.outdir}
    Datasets        : ${dataset_list.join(', ')}
    Tools           : ${tools_list.size()} tools
    Skip parsing    : ${params.skip_parsing}
    ================================================================
    """.stripIndent()
    
    // Create input channel
    if (params.skip_parsing) {
        // Use existing merged results
        input_ch = Channel
            .fromList(dataset_list)
            .map { dataset ->
                def merged_file = file("${params.input_dir}/${dataset}/analysis/results/${dataset}_merged_results.tsv")
                if (!merged_file.exists()) {
                    merged_file = file("${params.input_dir}/${dataset}/analysis/results/foxl2_merged_results.tsv")
                }
                if (!merged_file.exists()) {
                    log.error "ERROR: Merged results not found for dataset: ${dataset}"
                    exit 1
                }
                tuple(dataset, merged_file)
            }
    } else {
        // Parse from raw tool outputs
        input_ch = Channel
            .fromList(dataset_list)
            .map { dataset ->
                def dataset_dir = file("${params.input_dir}/${dataset}")
                
                // Get dataset-specific config or use defaults
                def config = dataset_configs.get(dataset, [:])
                
                // Ground truth file
                def gt_file = config.get('ground_truth', 'FOXL2_dataset.xlsx')
                def ground_truth = file("${dataset_dir}/${gt_file}")
                
                if (!ground_truth.exists()) {
                    // Try alternative names
                    ground_truth = file("${dataset_dir}/ground_truth.tsv")
                }
                
                if (!ground_truth.exists()) {
                    log.error "ERROR: Ground truth not found for dataset: ${dataset}"
                    exit 1
                }
                
                // Results directory
                def results_subdir = config.get('results_dir', 'results_fix')
                def results_dir = file("${dataset_dir}/${results_subdir}")
                
                if (!results_dir.exists()) {
                    log.error "ERROR: Results directory not found: ${results_dir}"
                    exit 1
                }
                
                // Tool files mapping
                def tool_files = config.get('tool_files', getDefaultToolFiles(dataset))
                def tool_files_json = groovy.json.JsonOutput.toJson(tool_files)
                
                tuple(dataset, ground_truth, results_dir, tool_files_json)
            }
    }
    
    // Run analysis
    ACMG_ANALYSIS(input_ch, tools_list, params.skip_parsing)
}

// Default tool files for FOXL2
def getDefaultToolFiles(dataset) {
    if (dataset.toLowerCase().contains('foxl2')) {
        return [
            'InterVar_2018': 'foxl2_hg38_intervar_20180118.txt',
            'InterVar_2025': 'foxl2_hg38_intervar_20250721.txt',
            'BIAS': 'foxl2_hg38_BIAS.tsv',
            'CharGer_Local': 'foxl2_hg38_CharGer_local_annotated_VEPv97.tsv',
            'CharGer_Online': 'foxl2_hg38_CharGer_online.tsv',
            'DiabloACMG': 'foxl2_hg38_DiabloACMG.tsv',
            'Exomiser': 'foxl2_hg38_exomiser.tsv',
            'Genebe': 'foxl2_hg38_genebe.vcf',
            'TAPES': 'foxl2_hg38_tapes.csv',
            'Franklin': 'foxl2_hg19_franklin.csv',
            'AutoGVP': 'foxl2_hg38_autogvp.tsv',
            'VIP-HL': 'foxl2_hg19_viphl.tsv'
        ]
    } else {
        // ClinGen or other datasets - need to be configured
        return [:]
    }
}

workflow.onComplete {
    log.info """
    ================================================================
    Pipeline completed!
    ================================================================
    Status   : ${workflow.success ? 'SUCCESS' : 'FAILED'}
    Duration : ${workflow.duration}
    Output   : ${params.outdir}
    ================================================================
    """.stripIndent()
}
