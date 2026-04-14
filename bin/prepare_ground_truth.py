#!/usr/bin/env python3
"""
Prepare Ground Truth from Annotated VCF

Extracts ground truth information from VCF files annotated with VEP and ClinVar data.
Creates both complete ground truth and NotVUS (non-VUS) versions.
"""

import pandas as pd
import argparse
from pathlib import Path
import re


def parse_vcf_to_ground_truth(vcf_file, dataset_name):
    """
    Parse VCF file to extract ground truth information
    
    Expects VCF with VEP annotations and ClinVar data
    """
    print(f"Parsing VCF: {vcf_file}")
    
    variants = []
    
    with open(vcf_file, 'r') as f:
        for line in f:
            if line.startswith('#'):
                continue
            
            fields = line.strip().split('\t')
            if len(fields) < 8:
                continue
            
            chrom = fields[0].replace('chr', '')
            pos = fields[1]
            ref = fields[3]
            alt = fields[4]
            info = fields[7]
            
            # Create variant key
            variant_key = f"{chrom}-{pos}-{ref}-{alt}"
            
            # Parse INFO field
            info_dict = {}
            for item in info.split(';'):
                if '=' in item:
                    key, value = item.split('=', 1)
                    info_dict[key] = value
            
            # Extract classification and ACMG codes
            classification = info_dict.get('CLASSIFICATION', '')
            met_codes = info_dict.get('MET_CODES', '')
            not_met_codes = info_dict.get('NOT_MET_CODES', '')
            gene = info_dict.get('GENE', '')
            
            # Extract VEP annotations if available
            vep_data = {}
            if 'CSQ' in info_dict:
                csq = info_dict['CSQ'].split('|')
                if len(csq) > 0:
                    vep_data['Consequence'] = csq[0] if len(csq) > 0 else ''
                    vep_data['Gene'] = csq[1] if len(csq) > 1 else gene
            
            variant = {
                'Chr': chrom,
                'Pos': int(pos),
                'Ref': ref,
                'Alt': alt,
                'Variant_Key': variant_key,
                'MET_CODES': met_codes,
                'NOT_MET_CODES': not_met_codes,
                'CLASSIFICATION': classification,
                'Standard_Classification': standardize_classification(classification),
                'GENE': vep_data.get('Gene', gene),
                'Dataset': dataset_name
            }
            
            variants.append(variant)
    
    df = pd.DataFrame(variants)
    print(f"  Extracted {len(df)} variants")
    
    return df


def standardize_classification(classification):
    """Standardize classification labels"""
    if not classification or classification == '.':
        return 'Unknown'
    
    classification = str(classification).upper().strip()
    
    if 'PATHOGENIC' in classification and 'LIKELY' not in classification:
        return 'Pathogenic'
    elif 'LIKELY' in classification and 'PATHOGENIC' in classification:
        return 'Likely_Pathogenic'
    elif 'UNCERTAIN' in classification or 'VUS' in classification:
        return 'VUS'
    elif 'LIKELY' in classification and 'BENIGN' in classification:
        return 'Likely_Benign'
    elif 'BENIGN' in classification and 'LIKELY' not in classification:
        return 'Benign'
    else:
        return 'Unknown'


def filter_notvus(df):
    """Filter out VUS variants to create NotVUS dataset"""
    notvus_df = df[df['Standard_Classification'] != 'VUS'].copy()
    print(f"  Filtered VUS: {len(df)} → {len(notvus_df)} variants")
    return notvus_df


def save_ground_truth(df, output_file, format='excel'):
    """Save ground truth to file"""
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    if format == 'excel':
        df.to_excel(output_file, index=False)
    else:
        df.to_csv(output_file, sep='\t', index=False)
    
    print(f"  Saved: {output_file}")


def create_master_ground_truth(ground_truth_files, output_file, format='excel', create_notvus=False):
    """Combine multiple ground truth files into a master ground truth"""
    print("\n" + "="*80)
    print("CREATING MASTER GROUND TRUTH")
    print("="*80)
    
    all_dfs = []
    
    for gt_file in ground_truth_files:
        print(f"\nLoading: {gt_file}")
        if gt_file.endswith('.xlsx'):
            df = pd.read_excel(gt_file)
        else:
            df = pd.read_csv(gt_file, sep='\t')
        
        print(f"  Variants: {len(df)}")
        if 'Dataset' in df.columns:
            print(f"  Dataset: {df['Dataset'].iloc[0] if len(df) > 0 else 'Unknown'}")
        
        all_dfs.append(df)
    
    # Combine all datasets
    master_df = pd.concat(all_dfs, ignore_index=True)
    print(f"\n{'='*80}")
    print(f"Combined {len(ground_truth_files)} datasets into master ground truth")
    print(f"Total variants: {len(master_df)}")
    
    if 'Dataset' in master_df.columns:
        print(f"\nDatasets included:")
        for dataset, count in master_df['Dataset'].value_counts().items():
            print(f"  - {dataset}: {count} variants")
    
    # Save master ground truth
    save_ground_truth(master_df, output_file, format)
    
    # Create NotVUS version if requested
    if create_notvus:
        master_notvus = filter_notvus(master_df)
        notvus_file = output_file.replace('_ground_truth', '_notvus_ground_truth')
        save_ground_truth(master_notvus, notvus_file, format)
    
    return master_df


def main():
    parser = argparse.ArgumentParser(description='Prepare ground truth from VCF or combine multiple ground truths')
    
    # Mode selection
    parser.add_argument('--mode', choices=['single', 'master'], default='single',
                       help='Mode: single (from VCF) or master (combine multiple)')
    
    # Single mode arguments
    parser.add_argument('--vcf', help='Input VCF file (for single mode)')
    parser.add_argument('--dataset', help='Dataset name (for single mode)')
    
    # Master mode arguments
    parser.add_argument('--input-files', nargs='+', 
                       help='Input ground truth files to combine (for master mode)')
    parser.add_argument('--master-name', default='master',
                       help='Name for master ground truth (default: master)')
    
    # Common arguments
    parser.add_argument('--output-dir', required=True, help='Output directory')
    parser.add_argument('--format', default='excel', choices=['excel', 'tsv'], 
                       help='Output format (default: excel)')
    parser.add_argument('--create-notvus', action='store_true',
                       help='Create NotVUS version (excludes VUS variants)')
    
    args = parser.parse_args()
    
    if args.mode == 'master':
        # Master ground truth mode
        if not args.input_files:
            parser.error("--input-files required for master mode")
        
        ext = 'xlsx' if args.format == 'excel' else 'tsv'
        output_file = Path(args.output_dir) / f"{args.master_name}_ground_truth.{ext}"
        
        master_df = create_master_ground_truth(
            args.input_files, 
            output_file, 
            args.format, 
            args.create_notvus
        )
        
        # Summary
        print("\n" + "="*80)
        print("MASTER GROUND TRUTH SUMMARY")
        print("="*80)
        print(f"Total variants: {len(master_df)}")
        
        if 'Standard_Classification' in master_df.columns:
            print(f"\nClassifications:")
            for cls, count in master_df['Standard_Classification'].value_counts().items():
                print(f"  {cls}: {count}")
        
        print("\n" + "="*80)
        return
    
    # Single VCF mode
    if not args.vcf or not args.dataset:
        parser.error("--vcf and --dataset required for single mode")
    
    args = parser.parse_args()
    
    print("="*80)
    print("GROUND TRUTH PREPARATION")
    print("="*80)
    
    # Parse VCF
    df = parse_vcf_to_ground_truth(args.vcf, args.dataset)
    
    # Save complete ground truth
    ext = 'xlsx' if args.format == 'excel' else 'tsv'
    output_all = Path(args.output_dir) / f"{args.dataset}_ground_truth.{ext}"
    save_ground_truth(df, output_all, args.format)
    
    # Create and save NotVUS version if requested
    if args.create_notvus:
        df_notvus = filter_notvus(df)
        output_notvus = Path(args.output_dir) / f"{args.dataset}_notvus_ground_truth.{ext}"
        save_ground_truth(df_notvus, output_notvus, args.format)
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Dataset: {args.dataset}")
    print(f"Total variants: {len(df)}")
    
    if 'Standard_Classification' in df.columns:
        print(f"\nClassifications:")
        for cls, count in df['Standard_Classification'].value_counts().items():
            print(f"  {cls}: {count}")
    
    if args.create_notvus:
        print(f"\nNotVUS variants: {len(df_notvus)}")
        print(f"VUS variants removed: {len(df) - len(df_notvus)}")
    
    print("\n" + "="*80)


if __name__ == '__main__':
    main()
