// VUS Misclassification Analysis Module

process ANALYZE_VUS_MISCLASSIFICATION {
    tag "$dataset_name"
    publishDir "${params.outdir}/${dataset_name}/results", mode: 'copy'
    
    input:
    tuple val(dataset_name), path(merged_results)
    val tools
    
    output:
    tuple val(dataset_name), path("vus_misclassification_metrics.tsv"), emit: metrics
    
    script:
    def tools_str = tools.join(',')
    """
    analyze_vus_misclassification.py \\
        --input ${merged_results} \\
        --output-metrics vus_misclassification_metrics.tsv \\
        --output-plot1 vus_rate.png \\
        --output-plot2 vus_by_category.png \\
        --output-plot3 correct_vs_vus.png \\
        --tools "${tools_str}" \\
        --title "VUS Misclassification - ${dataset_name}"
    """
}

process PLOT_VUS_ANALYSIS {
    tag "$dataset_name"
    publishDir "${params.outdir}/${dataset_name}/figures", mode: 'copy'
    
    input:
    tuple val(dataset_name), path(vus_metrics)
    
    output:
    tuple val(dataset_name), path("vus_*.png"), emit: plots
    
    script:
    """
    # Plots are generated in ANALYZE_VUS_MISCLASSIFICATION
    # This process just moves them to the figures directory
    mv vus_rate.png vus_overall_rate.png 2>/dev/null || true
    mv vus_by_category.png . 2>/dev/null || true
    mv correct_vs_vus.png . 2>/dev/null || true
    """
}
