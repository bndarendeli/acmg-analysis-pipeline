// Jaccard Similarity Analysis Module

process CALCULATE_JACCARD_SIMILARITY {
    tag "$dataset_name"
    publishDir "${params.outdir}/${dataset_name}/results", mode: 'copy'
    
    input:
    tuple val(dataset_name), path(merged_results)
    val tools
    
    output:
    tuple val(dataset_name), path("jaccard_per_variant.tsv"), emit: jaccard
    
    script:
    def tools_str = tools.join(',')
    def gt_col = dataset_name.contains('clingen') ? 'MET_CODES' : 'Ground_Truth_ACMG'
    """
    calculate_jaccard_similarity.py \\
        --input ${merged_results} \\
        --output jaccard_per_variant.tsv \\
        --tools "${tools_str}" \\
        --gt-col ${gt_col} \\
        --dataset ${dataset_name}
    """
}

process PLOT_JACCARD_SIMILARITY {
    tag "$dataset_name"
    publishDir "${params.outdir}/${dataset_name}/figures", mode: 'copy'
    
    input:
    tuple val(dataset_name), path(jaccard_tsv)
    
    output:
    tuple val(dataset_name), path("jaccard_per_variant.png"), emit: plot
    
    script:
    """
    plot_jaccard_similarity.py \\
        --input ${jaccard_tsv} \\
        --output jaccard_per_variant.png \\
        --title "Per-Variant Jaccard Similarity - ${dataset_name}"
    """
}
