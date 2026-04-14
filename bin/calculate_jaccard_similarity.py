#!/usr/bin/env python3
"""
Calculate per-variant Jaccard similarity for ACMG criteria
"""

import pandas as pd
import numpy as np
import argparse
import re
from pathlib import Path


def parse_criteria_string(criteria_str):
    """Parse ACMG criteria string into a set"""
    if pd.isna(criteria_str) or criteria_str in ['.', '', 'nan']:
        return set()
    
    criteria_str = str(criteria_str).strip()
    if not criteria_str:
        return set()
    
    # Updated pattern to match ACMG criteria including PVS1
    pattern = r'\b(PVS1|PS[1-4]|PM[1-6]|PP[1-5]|BA1|BS[1-4]|BP[1-7])\b'
    matches = re.findall(pattern, criteria_str, re.IGNORECASE)
    
    return set(m.upper() for m in matches)


def calculate_per_variant_jaccard(df, tools, gt_col='Ground_Truth_ACMG', dataset_name='dataset'):
    """Calculate per-variant Jaccard similarity"""
    results = []
    
    for tool in tools:
        criteria_col = f'{tool}_ACMG_Criteria'
        if criteria_col not in df.columns:
            continue
        
        jaccard_scores = []
        total_intersection = 0
        total_union = 0
        variants_analyzed = 0
        
        for idx, row in df.iterrows():
            gt_criteria = parse_criteria_string(row.get(gt_col, ''))
            tool_criteria = parse_criteria_string(row.get(criteria_col, ''))
            
            # Skip if both empty
            if not gt_criteria and not tool_criteria:
                continue
            
            # Calculate Jaccard for this variant
            intersection = len(gt_criteria & tool_criteria)
            union = len(gt_criteria | tool_criteria)
            
            jaccard = intersection / union if union > 0 else 0
            jaccard_scores.append(jaccard)
            
            total_intersection += intersection
            total_union += union
            variants_analyzed += 1
        
        # Average Jaccard across all variants
        avg_jaccard = np.mean(jaccard_scores) if jaccard_scores else 0
        aggregate_jaccard = total_intersection / total_union if total_union > 0 else 0
        
        results.append({
            'Tool': tool,
            'Dataset': dataset_name,
            'Avg_Jaccard_Per_Variant': avg_jaccard,
            'Aggregate_Jaccard': aggregate_jaccard,
            'Variants_Analyzed': variants_analyzed,
            'Total_Intersection': total_intersection,
            'Total_Union': total_union
        })
    
    return pd.DataFrame(results)


def main():
    parser = argparse.ArgumentParser(description='Calculate per-variant Jaccard similarity')
    parser.add_argument('--input', required=True, help='Input merged results TSV')
    parser.add_argument('--output', required=True, help='Output Jaccard TSV')
    parser.add_argument('--tools', required=True, help='Comma-separated list of tools')
    parser.add_argument('--gt-col', default='Ground_Truth_ACMG', help='Ground truth ACMG column')
    parser.add_argument('--dataset', default='dataset', help='Dataset name')
    
    args = parser.parse_args()
    
    # Load data
    df = pd.read_csv(args.input, sep='\t')
    tools = [t.strip() for t in args.tools.split(',')]
    
    # Calculate Jaccard
    results = calculate_per_variant_jaccard(df, tools, args.gt_col, args.dataset)
    
    # Save results
    results.to_csv(args.output, sep='\t', index=False)
    print(f"Calculated Jaccard for {len(results)} tools")
    print(f"Saved to: {args.output}")


if __name__ == '__main__':
    main()
