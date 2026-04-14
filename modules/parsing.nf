// Parsing and Merging Module

process PARSE_AND_MERGE {
    tag "$dataset_name"
    publishDir "${params.outdir}/${dataset_name}/parsed", mode: 'copy'
    
    input:
    tuple val(dataset_name), path(ground_truth), path(results_dir), val(tool_files_json)
    
    output:
    tuple val(dataset_name), path("${dataset_name}_merged_results.tsv"), emit: merged_results
    
    script:
    """
    parse_and_merge.py \\
        --ground-truth ${ground_truth} \\
        --results-dir ${results_dir} \\
        --tool-files '${tool_files_json}' \\
        --output ${dataset_name}_merged_results.tsv \\
        --dataset-type ${dataset_name.contains('clingen') ? 'clingen' : 'foxl2'}
    """
}
