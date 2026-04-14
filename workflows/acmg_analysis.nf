// Main ACMG Analysis Workflow

include { PARSE_AND_MERGE } from '../modules/parsing'
include { CALCULATE_CLASSIFICATION_ACCURACY; PLOT_CLASSIFICATION_ACCURACY } from '../modules/classification_accuracy'
include { CALCULATE_JACCARD_SIMILARITY; PLOT_JACCARD_SIMILARITY } from '../modules/jaccard_similarity'
include { ANALYZE_VUS_MISCLASSIFICATION } from '../modules/vus_analysis'

workflow ACMG_ANALYSIS {
    take:
    input_ch           // channel: [dataset_name, ground_truth, results_dir, tool_files_json]
    tools              // list of tool names
    skip_parsing       // boolean: skip parsing if merged results already exist
    
    main:
    if (skip_parsing) {
        // Use pre-existing merged results
        merged_results_ch = input_ch
    } else {
        // Parse and merge tool results
        PARSE_AND_MERGE(input_ch)
        merged_results_ch = PARSE_AND_MERGE.out.merged_results
    }
    
    // Classification Accuracy Analysis
    CALCULATE_CLASSIFICATION_ACCURACY(merged_results_ch, tools)
    PLOT_CLASSIFICATION_ACCURACY(CALCULATE_CLASSIFICATION_ACCURACY.out.accuracy)
    
    // Jaccard Similarity Analysis
    CALCULATE_JACCARD_SIMILARITY(merged_results_ch, tools)
    PLOT_JACCARD_SIMILARITY(CALCULATE_JACCARD_SIMILARITY.out.jaccard)
    
    // VUS Misclassification Analysis
    ANALYZE_VUS_MISCLASSIFICATION(merged_results_ch, tools)
    
    emit:
    merged_results = merged_results_ch
    classification_accuracy = CALCULATE_CLASSIFICATION_ACCURACY.out.accuracy
    classification_plots = PLOT_CLASSIFICATION_ACCURACY.out.plots
    jaccard_similarity = CALCULATE_JACCARD_SIMILARITY.out.jaccard
    jaccard_plots = PLOT_JACCARD_SIMILARITY.out.plot
    vus_metrics = ANALYZE_VUS_MISCLASSIFICATION.out.metrics
}
