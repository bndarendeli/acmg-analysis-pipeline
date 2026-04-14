// Ground Truth Preparation Module

process PREPARE_GROUND_TRUTH {
    tag "$dataset_name"
    publishDir "${params.outdir}/${dataset_name}/ground_truth", mode: 'copy'
    
    input:
    tuple val(dataset_name), path(vcf_file)
    val create_notvus
    
    output:
    tuple val(dataset_name), path("${dataset_name}_ground_truth.xlsx"), emit: ground_truth
    tuple val(dataset_name), path("${dataset_name}_notvus_ground_truth.xlsx"), optional: true, emit: ground_truth_notvus
    
    script:
    def notvus_flag = create_notvus ? '--create-notvus' : ''
    """
    prepare_ground_truth.py \\
        --vcf ${vcf_file} \\
        --dataset ${dataset_name} \\
        --output-dir . \\
        --format excel \\
        ${notvus_flag}
    """
}

process CONVERT_GROUND_TRUTH_TO_TSV {
    tag "$dataset_name"
    publishDir "${params.outdir}/${dataset_name}/ground_truth", mode: 'copy'
    
    input:
    tuple val(dataset_name), path(ground_truth_excel)
    
    output:
    tuple val(dataset_name), path("${dataset_name}_ground_truth.tsv"), emit: ground_truth_tsv
    
    script:
    """
    #!/usr/bin/env python3
    import pandas as pd
    
    df = pd.read_excel('${ground_truth_excel}')
    df.to_csv('${dataset_name}_ground_truth.tsv', sep='\\t', index=False)
    """
}
