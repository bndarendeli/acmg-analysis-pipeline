#!/usr/bin/env python3
"""
Create classification accuracy visualization plots
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import argparse
from pathlib import Path


def create_accuracy_barplot(accuracy_df, output_file, title='Classification Accuracy'):
    """Create accuracy comparison bar plot"""
    accuracy_sorted = accuracy_df.sort_values('Accuracy', ascending=False)
    
    fig, ax = plt.subplots(figsize=(12, 8))
    bars = ax.barh(accuracy_sorted['Tool'], accuracy_sorted['Accuracy'],
                   color='steelblue', edgecolor='black', linewidth=0.5)
    
    for bar, val in zip(bars, accuracy_sorted['Accuracy']):
        ax.text(val + 0.01, bar.get_y() + bar.get_height()/2, 
                f'{val:.3f}', va='center', fontsize=10, fontweight='bold')
    
    ax.set_xlabel('Classification Accuracy', fontsize=12, fontweight='bold')
    ax.set_ylabel('Tool', fontsize=12, fontweight='bold')
    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    ax.set_xlim(0, 1.0)
    ax.grid(axis='x', alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: {output_file}")


def create_recall_comparison(accuracy_df, output_file, title='Pathogenic vs Benign Recall'):
    """Create pathogenic vs benign recall comparison"""
    accuracy_df['Avg_Recall'] = (accuracy_df['Pathogenic_Recall'] + accuracy_df['Benign_Recall']) / 2
    accuracy_sorted = accuracy_df.sort_values('Avg_Recall', ascending=False)
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    x = np.arange(len(accuracy_sorted))
    width = 0.35
    
    bars1 = ax.bar(x - width/2, accuracy_sorted['Pathogenic_Recall'], width,
                   label='Pathogenic Recall', color='#d62728', edgecolor='black', linewidth=0.5)
    bars2 = ax.bar(x + width/2, accuracy_sorted['Benign_Recall'], width,
                   label='Benign Recall', color='#2ca02c', edgecolor='black', linewidth=0.5)
    
    ax.set_xlabel('Tool', fontsize=12, fontweight='bold')
    ax.set_ylabel('Recall', fontsize=12, fontweight='bold')
    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(accuracy_sorted['Tool'], rotation=45, ha='right')
    ax.legend(fontsize=10)
    ax.set_ylim(0, 1.0)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: {output_file}")


def main():
    parser = argparse.ArgumentParser(description='Plot classification accuracy')
    parser.add_argument('--input', required=True, help='Input accuracy TSV')
    parser.add_argument('--output-accuracy', required=True, help='Output accuracy plot')
    parser.add_argument('--output-recall', required=True, help='Output recall plot')
    parser.add_argument('--title', default='Classification Accuracy', help='Plot title prefix')
    
    args = parser.parse_args()
    
    # Load data
    df = pd.read_csv(args.input, sep='\t')
    
    # Create plots
    create_accuracy_barplot(df, args.output_accuracy, args.title)
    create_recall_comparison(df, args.output_recall, f'{args.title} - Recall')


if __name__ == '__main__':
    main()
