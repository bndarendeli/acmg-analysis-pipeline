#!/usr/bin/env python3
"""
Calculate classification accuracy metrics for ACMG tool predictions
"""

import pandas as pd
import numpy as np
import argparse
from pathlib import Path
from sklearn.metrics import accuracy_score, f1_score


def standardize_classification(classification: str) -> str:
    """Standardize classification labels"""
    if pd.isna(classification) or classification in ['.', '', 'nan', 'Unknown']:
        return 'Unknown'
    
    classification = str(classification).upper().strip()
    
    if classification in ['P', 'PATHOGENIC']:
        return 'Pathogenic'
    elif classification in ['LP', 'LIKELY_PATHOGENIC', 'LIKELYPATHOGENIC']:
        return 'Likely_Pathogenic'
    elif classification in ['VUS', 'UNCERTAIN_SIGNIFICANCE', 'UNCERTAINSIGNIFICANCE', 'US']:
        return 'VUS'
    elif classification in ['LB', 'LIKELY_BENIGN', 'LIKELYBENIGN']:
        return 'Likely_Benign'
    elif classification in ['B', 'BENIGN']:
        return 'Benign'
    else:
        return 'Unknown'


def calculate_metrics(df, tools, gt_col='Ground_Truth_Class'):
    """Calculate accuracy metrics for all tools"""
    results = []
    
    # Standardize ground truth
    df['GT_Std'] = df[gt_col].apply(standardize_classification)
    
    for tool in tools:
        class_col = f'{tool}_Classification'
        if class_col not in df.columns:
            continue
        
        # Standardize tool classification
        df[f'{tool}_Std'] = df[class_col].apply(standardize_classification)
        
        # Filter valid predictions
        valid_mask = (df['GT_Std'] != 'Unknown') & (df[f'{tool}_Std'] != 'Unknown')
        gt_valid = df.loc[valid_mask, 'GT_Std']
        pred_valid = df.loc[valid_mask, f'{tool}_Std']
        
        if len(gt_valid) == 0:
            continue
        
        # Calculate metrics
        accuracy = accuracy_score(gt_valid, pred_valid)
        f1 = f1_score(gt_valid, pred_valid, average='weighted', zero_division=0)
        
        # Pathogenic recall
        gt_path = gt_valid.isin(['Pathogenic', 'Likely_Pathogenic'])
        pred_path = pred_valid.isin(['Pathogenic', 'Likely_Pathogenic'])
        path_recall = (gt_path & pred_path).sum() / gt_path.sum() if gt_path.sum() > 0 else 0
        
        # Benign recall
        gt_benign = gt_valid.isin(['Benign', 'Likely_Benign'])
        pred_benign = pred_valid.isin(['Benign', 'Likely_Benign'])
        benign_recall = (gt_benign & pred_benign).sum() / gt_benign.sum() if gt_benign.sum() > 0 else 0
        
        results.append({
            'Tool': tool,
            'Total_Variants': len(gt_valid),
            'Accuracy': accuracy,
            'F1_Score': f1,
            'Pathogenic_Recall': path_recall,
            'Benign_Recall': benign_recall
        })
    
    return pd.DataFrame(results)


def main():
    parser = argparse.ArgumentParser(description='Calculate classification accuracy')
    parser.add_argument('--input', required=True, help='Input merged results TSV')
    parser.add_argument('--output', required=True, help='Output accuracy TSV')
    parser.add_argument('--tools', required=True, help='Comma-separated list of tools')
    parser.add_argument('--gt-col', default='Ground_Truth_Class', help='Ground truth column name')
    
    args = parser.parse_args()
    
    # Load data
    df = pd.read_csv(args.input, sep='\t')
    tools = [t.strip() for t in args.tools.split(',')]
    
    # Calculate metrics
    results = calculate_metrics(df, tools, args.gt_col)
    
    # Save results
    results.to_csv(args.output, sep='\t', index=False)
    print(f"Calculated accuracy for {len(results)} tools")
    print(f"Saved to: {args.output}")


if __name__ == '__main__':
    main()
