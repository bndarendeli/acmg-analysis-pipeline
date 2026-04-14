#!/usr/bin/env python3
"""
VUS Misclassification Analysis

Analyzes how tools incorrectly assign VUS to variants that are NOT VUS in ground truth.
Focuses on non-VUS variants (P, LP, B, LB) and evaluates VUS over-assignment.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import argparse
from pathlib import Path


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


def analyze_vus_misclassification(df, tools):
    """
    Analyze VUS misclassification for non-VUS ground truth variants
    
    Returns metrics on how often tools incorrectly assign VUS to:
    - Pathogenic/Likely Pathogenic variants
    - Benign/Likely Benign variants
    """
    # Standardize ground truth
    df['GT_Std'] = df['Ground_Truth_Classification'].apply(standardize_classification)
    
    # Filter to non-VUS ground truth variants only
    non_vus_df = df[df['GT_Std'].isin(['Pathogenic', 'Likely_Pathogenic', 'Benign', 'Likely_Benign'])].copy()
    
    if len(non_vus_df) == 0:
        print("Warning: No non-VUS variants found in ground truth")
        return pd.DataFrame()
    
    print(f"\nAnalyzing {len(non_vus_df)} non-VUS ground truth variants:")
    print(f"  Pathogenic/LP: {(non_vus_df['GT_Std'].isin(['Pathogenic', 'Likely_Pathogenic'])).sum()}")
    print(f"  Benign/LB: {(non_vus_df['GT_Std'].isin(['Benign', 'Likely_Benign'])).sum()}")
    
    results = []
    
    for tool in tools:
        class_col = f'{tool}_Classification'
        if class_col not in df.columns:
            continue
        
        # Standardize tool classification
        non_vus_df[f'{tool}_Std'] = non_vus_df[class_col].apply(standardize_classification)
        
        # Filter valid predictions
        valid_mask = non_vus_df[f'{tool}_Std'] != 'Unknown'
        valid_df = non_vus_df[valid_mask]
        
        if len(valid_df) == 0:
            continue
        
        # Calculate VUS misclassification rates
        total_non_vus = len(valid_df)
        vus_assigned = (valid_df[f'{tool}_Std'] == 'VUS').sum()
        vus_rate = vus_assigned / total_non_vus if total_non_vus > 0 else 0
        
        # Pathogenic variants called VUS
        path_df = valid_df[valid_df['GT_Std'].isin(['Pathogenic', 'Likely_Pathogenic'])]
        path_vus = (path_df[f'{tool}_Std'] == 'VUS').sum()
        path_vus_rate = path_vus / len(path_df) if len(path_df) > 0 else 0
        
        # Benign variants called VUS
        benign_df = valid_df[valid_df['GT_Std'].isin(['Benign', 'Likely_Benign'])]
        benign_vus = (benign_df[f'{tool}_Std'] == 'VUS').sum()
        benign_vus_rate = benign_vus / len(benign_df) if len(benign_df) > 0 else 0
        
        # Correct non-VUS classification (not VUS)
        correct_non_vus = total_non_vus - vus_assigned
        correct_rate = correct_non_vus / total_non_vus if total_non_vus > 0 else 0
        
        results.append({
            'Tool': tool,
            'Total_NonVUS_Variants': total_non_vus,
            'VUS_Assigned': vus_assigned,
            'VUS_Assignment_Rate': vus_rate,
            'Correct_NonVUS_Rate': correct_rate,
            'Pathogenic_Total': len(path_df),
            'Pathogenic_Called_VUS': path_vus,
            'Pathogenic_VUS_Rate': path_vus_rate,
            'Benign_Total': len(benign_df),
            'Benign_Called_VUS': benign_vus,
            'Benign_VUS_Rate': benign_vus_rate
        })
    
    return pd.DataFrame(results)


def create_vus_misclassification_plot(vus_df, output_file, title='VUS Over-Assignment Rate'):
    """Create bar plot showing VUS misclassification rates"""
    vus_sorted = vus_df.sort_values('VUS_Assignment_Rate', ascending=True)
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    bars = ax.barh(vus_sorted['Tool'], vus_sorted['VUS_Assignment_Rate'] * 100,
                   color='#ff7f0e', edgecolor='black', linewidth=0.5)
    
    for bar, val in zip(bars, vus_sorted['VUS_Assignment_Rate']):
        ax.text(val * 100 + 1, bar.get_y() + bar.get_height()/2, 
                f'{val*100:.1f}%', va='center', fontsize=10, fontweight='bold')
    
    ax.set_xlabel('VUS Over-Assignment Rate (%)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Tool', fontsize=12, fontweight='bold')
    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    ax.set_xlim(0, 100)
    ax.grid(axis='x', alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: {output_file}")


def create_vus_by_category_plot(vus_df, output_file, title='VUS Assignment by Variant Category'):
    """Create grouped bar plot showing VUS rates for pathogenic vs benign"""
    vus_df['Avg_VUS_Rate'] = (vus_df['Pathogenic_VUS_Rate'] + vus_df['Benign_VUS_Rate']) / 2
    vus_sorted = vus_df.sort_values('Avg_VUS_Rate', ascending=False)
    
    fig, ax = plt.subplots(figsize=(14, 8))
    
    x = np.arange(len(vus_sorted))
    width = 0.35
    
    bars1 = ax.bar(x - width/2, vus_sorted['Pathogenic_VUS_Rate'] * 100, width,
                   label='Pathogenic/LP → VUS', color='#d62728', edgecolor='black', linewidth=0.5)
    bars2 = ax.bar(x + width/2, vus_sorted['Benign_VUS_Rate'] * 100, width,
                   label='Benign/LB → VUS', color='#2ca02c', edgecolor='black', linewidth=0.5)
    
    ax.set_xlabel('Tool', fontsize=12, fontweight='bold')
    ax.set_ylabel('VUS Assignment Rate (%)', fontsize=12, fontweight='bold')
    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(vus_sorted['Tool'], rotation=45, ha='right')
    ax.legend(fontsize=10, loc='upper right')
    ax.set_ylim(0, 100)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: {output_file}")


def create_correct_vs_vus_plot(vus_df, output_file, title='Correct Classification vs VUS Over-Assignment'):
    """Create stacked bar plot showing correct vs VUS assignment"""
    vus_sorted = vus_df.sort_values('Correct_NonVUS_Rate', ascending=False)
    
    fig, ax = plt.subplots(figsize=(14, 8))
    
    x = np.arange(len(vus_sorted))
    
    bars1 = ax.bar(x, vus_sorted['Correct_NonVUS_Rate'] * 100,
                   label='Correct (Non-VUS)', color='#1f77b4', edgecolor='black', linewidth=0.5)
    bars2 = ax.bar(x, vus_sorted['VUS_Assignment_Rate'] * 100,
                   bottom=vus_sorted['Correct_NonVUS_Rate'] * 100,
                   label='Incorrect (VUS)', color='#ff7f0e', edgecolor='black', linewidth=0.5)
    
    ax.set_xlabel('Tool', fontsize=12, fontweight='bold')
    ax.set_ylabel('Percentage (%)', fontsize=12, fontweight='bold')
    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(vus_sorted['Tool'], rotation=45, ha='right')
    ax.legend(fontsize=10)
    ax.set_ylim(0, 100)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Add percentage labels
    for i, (correct, vus) in enumerate(zip(vus_sorted['Correct_NonVUS_Rate'], vus_sorted['VUS_Assignment_Rate'])):
        if correct > 0.05:
            ax.text(i, correct * 50, f'{correct*100:.0f}%', ha='center', va='center', fontweight='bold', fontsize=9)
        if vus > 0.05:
            ax.text(i, (correct + vus/2) * 100, f'{vus*100:.0f}%', ha='center', va='center', fontweight='bold', fontsize=9)
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: {output_file}")


def main():
    parser = argparse.ArgumentParser(description='Analyze VUS misclassification')
    parser.add_argument('--input', required=True, help='Input merged results TSV')
    parser.add_argument('--output-metrics', required=True, help='Output VUS metrics TSV')
    parser.add_argument('--output-plot1', required=True, help='Output VUS rate plot')
    parser.add_argument('--output-plot2', required=True, help='Output VUS by category plot')
    parser.add_argument('--output-plot3', required=True, help='Output correct vs VUS plot')
    parser.add_argument('--tools', required=True, help='Comma-separated list of tools')
    parser.add_argument('--title', default='VUS Misclassification Analysis', help='Plot title prefix')
    
    args = parser.parse_args()
    
    # Load data
    df = pd.read_csv(args.input, sep='\t')
    tools = [t.strip() for t in args.tools.split(',')]
    
    print("="*80)
    print("VUS MISCLASSIFICATION ANALYSIS")
    print("="*80)
    print(f"Total variants: {len(df)}")
    
    # Analyze VUS misclassification
    vus_metrics = analyze_vus_misclassification(df, tools)
    
    if len(vus_metrics) == 0:
        print("No VUS metrics calculated")
        return
    
    # Save metrics
    vus_metrics.to_csv(args.output_metrics, sep='\t', index=False)
    print(f"\nSaved metrics: {args.output_metrics}")
    
    # Create plots
    print("\nCreating visualizations...")
    create_vus_misclassification_plot(vus_metrics, args.output_plot1, 
                                      f'{args.title} - Overall VUS Rate')
    create_vus_by_category_plot(vus_metrics, args.output_plot2,
                                f'{args.title} - By Category')
    create_correct_vs_vus_plot(vus_metrics, args.output_plot3,
                               f'{args.title} - Correct vs VUS')
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY - VUS OVER-ASSIGNMENT")
    print("="*80)
    print(f"\nTop 5 Tools with Lowest VUS Over-Assignment:")
    top_correct = vus_metrics.nsmallest(5, 'VUS_Assignment_Rate')
    for i, row in enumerate(top_correct.itertuples(), 1):
        print(f"  {i}. {row.Tool:<20} VUS Rate: {row.VUS_Assignment_Rate*100:.1f}% (Correct: {row.Correct_NonVUS_Rate*100:.1f}%)")
    
    print(f"\nTop 5 Tools with Highest VUS Over-Assignment:")
    top_vus = vus_metrics.nlargest(5, 'VUS_Assignment_Rate')
    for i, row in enumerate(top_vus.itertuples(), 1):
        print(f"  {i}. {row.Tool:<20} VUS Rate: {row.VUS_Assignment_Rate*100:.1f}%")
    
    print("\n" + "="*80)


if __name__ == '__main__':
    main()
