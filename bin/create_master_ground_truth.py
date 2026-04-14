#!/usr/bin/env python3
"""
Create Master Ground Truth

Combines multiple individual dataset ground truth files into a single master ground truth.
Useful for cross-dataset analysis and comparison.
"""

import pandas as pd
import argparse
from pathlib import Path


def load_ground_truth(file_path):
    """Load ground truth from Excel or TSV"""
    if file_path.endswith('.xlsx'):
        return pd.read_excel(file_path)
    else:
        return pd.read_csv(file_path, sep='\t')


def filter_notvus(df):
    """Filter out VUS variants"""
    if 'Standard_Classification' in df.columns:
        notvus_df = df[df['Standard_Classification'] != 'VUS'].copy()
    elif 'CLASSIFICATION' in df.columns:
        notvus_df = df[~df['CLASSIFICATION'].str.contains('Uncertain', case=False, na=False)].copy()
    else:
        print("Warning: No classification column found, returning all variants")
        notvus_df = df.copy()
    
    print(f"  Filtered VUS: {len(df)} → {len(notvus_df)} variants")
    return notvus_df


def create_master_ground_truth(input_files, output_file, create_notvus=False):
    """Combine multiple ground truth files into master"""
    print("="*80)
    print("CREATING MASTER GROUND TRUTH")
    print("="*80)
    
    all_dfs = []
    dataset_info = []
    
    for file_path in input_files:
        print(f"\nLoading: {file_path}")
        df = load_ground_truth(file_path)
        
        # Extract dataset name from filename if not in data
        if 'Dataset' not in df.columns:
            dataset_name = Path(file_path).stem.replace('_ground_truth', '').replace('_notvus', '')
            df['Dataset'] = dataset_name
        
        dataset_name = df['Dataset'].iloc[0] if len(df) > 0 else 'Unknown'
        print(f"  Dataset: {dataset_name}")
        print(f"  Variants: {len(df)}")
        
        dataset_info.append({
            'dataset': dataset_name,
            'variants': len(df),
            'file': file_path
        })
        
        all_dfs.append(df)
    
    # Combine all datasets
    master_df = pd.concat(all_dfs, ignore_index=True)
    
    print(f"\n{'='*80}")
    print(f"COMBINED {len(input_files)} DATASETS")
    print(f"{'='*80}")
    print(f"Total variants: {len(master_df)}")
    
    if 'Dataset' in master_df.columns:
        print(f"\nDatasets included:")
        for dataset, count in master_df['Dataset'].value_counts().items():
            print(f"  - {dataset}: {count:,} variants")
    
    # Classification distribution
    if 'Standard_Classification' in master_df.columns:
        print(f"\nClassification distribution:")
        for cls, count in master_df['Standard_Classification'].value_counts().items():
            pct = (count / len(master_df)) * 100
            print(f"  - {cls}: {count:,} ({pct:.1f}%)")
    elif 'CLASSIFICATION' in master_df.columns:
        print(f"\nClassification distribution:")
        for cls, count in master_df['CLASSIFICATION'].value_counts().items():
            pct = (count / len(master_df)) * 100
            print(f"  - {cls}: {count:,} ({pct:.1f}%)")
    
    # Save master ground truth
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    if output_file.endswith('.xlsx'):
        master_df.to_excel(output_file, index=False)
    else:
        master_df.to_csv(output_file, sep='\t', index=False)
    
    print(f"\n✓ Saved master ground truth: {output_file}")
    
    # Create NotVUS version if requested
    if create_notvus:
        print(f"\nCreating NotVUS version...")
        master_notvus = filter_notvus(master_df)
        
        notvus_file = str(output_file).replace('_ground_truth', '_notvus_ground_truth')
        if notvus_file.endswith('.xlsx'):
            master_notvus.to_excel(notvus_file, index=False)
        else:
            master_notvus.to_csv(notvus_file, sep='\t', index=False)
        
        print(f"✓ Saved NotVUS master ground truth: {notvus_file}")
    
    return master_df


def main():
    parser = argparse.ArgumentParser(
        description='Create master ground truth by combining multiple datasets',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Combine multiple ground truth files
  create_master_ground_truth.py \\
    --input-files clingen_gt.xlsx foxl2_gt.xlsx hgmd_gt.xlsx \\
    --output master_ground_truth.xlsx \\
    --create-notvus
  
  # Combine with TSV output
  create_master_ground_truth.py \\
    --input-files *.xlsx \\
    --output master_ground_truth.tsv \\
    --create-notvus
        """
    )
    
    parser.add_argument('--input-files', nargs='+', required=True,
                       help='Input ground truth files to combine (Excel or TSV)')
    parser.add_argument('--output', required=True,
                       help='Output master ground truth file (.xlsx or .tsv)')
    parser.add_argument('--create-notvus', action='store_true',
                       help='Create NotVUS version (excludes VUS variants)')
    
    args = parser.parse_args()
    
    # Validate input files
    for file_path in args.input_files:
        if not Path(file_path).exists():
            print(f"Error: File not found: {file_path}")
            return 1
    
    # Create master ground truth
    create_master_ground_truth(args.input_files, args.output, args.create_notvus)
    
    print("\n" + "="*80)
    print("✅ MASTER GROUND TRUTH CREATED SUCCESSFULLY")
    print("="*80)
    
    return 0


if __name__ == '__main__':
    exit(main())
