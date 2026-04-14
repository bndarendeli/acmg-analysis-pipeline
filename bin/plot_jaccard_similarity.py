#!/usr/bin/env python3
"""
Create Jaccard similarity visualization plots
"""

import pandas as pd
import matplotlib.pyplot as plt
import argparse
from pathlib import Path


def create_jaccard_barplot(jaccard_df, output_file, title='Per-Variant Jaccard Similarity'):
    """Create Jaccard similarity bar plot"""
    jaccard_sorted = jaccard_df.sort_values('Avg_Jaccard_Per_Variant', ascending=False)
    
    fig, ax = plt.subplots(figsize=(12, 8))
    bars = ax.barh(jaccard_sorted['Tool'], jaccard_sorted['Avg_Jaccard_Per_Variant'],
                   color='steelblue', edgecolor='black', linewidth=0.5)
    
    for bar, val in zip(bars, jaccard_sorted['Avg_Jaccard_Per_Variant']):
        ax.text(val + 0.01, bar.get_y() + bar.get_height()/2, 
                f'{val:.3f}', va='center', fontsize=10, fontweight='bold')
    
    ax.set_xlabel('Average Jaccard Similarity (Per-Variant)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Tool', fontsize=12, fontweight='bold')
    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    ax.set_xlim(0, 1.0)
    ax.grid(axis='x', alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: {output_file}")


def main():
    parser = argparse.ArgumentParser(description='Plot Jaccard similarity')
    parser.add_argument('--input', required=True, help='Input Jaccard TSV')
    parser.add_argument('--output', required=True, help='Output plot file')
    parser.add_argument('--title', default='Per-Variant Jaccard Similarity', help='Plot title')
    
    args = parser.parse_args()
    
    # Load data
    df = pd.read_csv(args.input, sep='\t')
    
    # Create plot
    create_jaccard_barplot(df, args.output, args.title)


if __name__ == '__main__':
    main()
