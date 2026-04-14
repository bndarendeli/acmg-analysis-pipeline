// Classification Accuracy Analysis Module

process CALCULATE_CLASSIFICATION_ACCURACY {
    tag "$dataset_name"
    publishDir "${params.outdir}/${dataset_name}/results", mode: 'copy'
    
    input:
    tuple val(dataset_name), path(merged_results)
    val tools
    
    output:
    tuple val(dataset_name), path("classification_accuracy.tsv"), emit: accuracy
    
    script:
    def tools_str = tools.join(',')
    """
    calculate_classification_accuracy.py \\
        --input ${merged_results} \\
        --output classification_accuracy.tsv \\
        --tools "${tools_str}" \\
        --gt-col Ground_Truth_Classification
    """
}

process PLOT_CLASSIFICATION_ACCURACY {
    tag "$dataset_name"
    publishDir "${params.outdir}/${dataset_name}/figures", mode: 'copy'
    
    input:
    tuple val(dataset_name), path(accuracy_tsv)
    
    output:
    tuple val(dataset_name), path("classification_accuracy.png"), path("pathogenic_benign_recall.png"), emit: plots
    
    script:
    """
    plot_classification_accuracy.py \\
        --input ${accuracy_tsv} \\
        --output-accuracy classification_accuracy.png \\
        --output-recall pathogenic_benign_recall.png \\
        --title "Classification Accuracy - ${dataset_name}"
    """
}
