#!/usr/bin/env python3
"""
Parse tool results and merge with ground truth
End-to-end parsing for ACMG analysis pipeline
"""

import sys
import pandas as pd
import argparse
from pathlib import Path

# Add parsers to path
sys.path.insert(0, str(Path(__file__).parent))
from parsers.parser_factory import ParserFactory


def load_ground_truth(ground_truth_file, dataset_type='foxl2'):
    """Load ground truth from Excel or TSV file"""
    print(f"Loading ground truth from: {ground_truth_file}")
    
    if ground_truth_file.endswith('.xlsx'):
        # FOXL2 format
        df = pd.read_excel(ground_truth_file)
        
        variant_keys_hg38 = []
        variant_keys_hg19 = []
        
        for idx, row in df.iterrows():
            # hg38 variant key
            if pd.isna(row.get('hg38', '')) or not row.get('hg38', ''):
                variant_keys_hg38.append('')
            else:
                parts = str(row['hg38']).split('-')
                if len(parts) == 4:
                    chrom, pos, ref, alt = parts
                    chrom = chrom.replace('chr', '')
                    variant_key = f"{chrom}-{pos}-{ref}-{alt}"
                    variant_keys_hg38.append(variant_key)
                else:
                    variant_keys_hg38.append('')
            
            # hg19 variant key
            if pd.isna(row.get('hg19', '')) or not row.get('hg19', ''):
                variant_keys_hg19.append('')
            else:
                parts = str(row['hg19']).split('-')
                if len(parts) == 4:
                    chrom, pos, ref, alt = parts
                    chrom = chrom.replace('chr', '')
                    variant_key = f"{chrom}-{pos}-{ref}-{alt}"
                    variant_keys_hg19.append(variant_key)
                else:
                    variant_keys_hg19.append('')
        
        ground_truth = pd.DataFrame({
            'Variant_Key': variant_keys_hg38,
            'Variant_Key_hg19': variant_keys_hg19,
            'HGVS': df.get('HGVS', ''),
            'Ground_Truth_Classification': df.get('Classification', ''),
            'Ground_Truth_ACMG': df.get('ACMG-AMP classification', '')
        })
        
        # Remove rows without valid variant keys
        ground_truth = ground_truth[ground_truth['Variant_Key'] != '']
        ground_truth = ground_truth.drop_duplicates(subset=['Variant_Key'], keep='first')
        
    else:
        # ClinGen TSV format
        df = pd.read_csv(ground_truth_file, sep='\t')
        ground_truth = df.copy()
        
        # Ensure required columns exist
        if 'Variant_Key' not in ground_truth.columns:
            # Create variant key from available columns
            if all(col in df.columns for col in ['CHROM', 'POS', 'REF', 'ALT']):
                ground_truth['Variant_Key'] = (
                    df['CHROM'].astype(str) + '-' +
                    df['POS'].astype(str) + '-' +
                    df['REF'].astype(str) + '-' +
                    df['ALT'].astype(str)
                )
    
    print(f"  Loaded {len(ground_truth)} unique ground truth variants")
    return ground_truth


def parse_tool_results(tool_files_dict, results_dir):
    """Parse all tool result files"""
    results_dir = Path(results_dir)
    tool_results = {}
    
    for tool_name, filename in tool_files_dict.items():
        file_path = results_dir / filename
        
        if not file_path.exists():
            print(f"  Warning: {filename} not found, skipping {tool_name}")
            continue
        
        print(f"Parsing {tool_name}...")
        try:
            parser = ParserFactory.get_parser(tool_name, str(file_path))
            tool_df = parser.parse(str(file_path))
            
            if tool_df is not None and len(tool_df) > 0:
                # Remove duplicates
                tool_df = tool_df.drop_duplicates(subset=['Variant_Key'], keep='first')
                print(f"  Parsed {len(tool_df)} unique variants")
                tool_results[tool_name] = tool_df
            else:
                print(f"  Warning: No results parsed for {tool_name}")
        except Exception as e:
            print(f"  Error parsing {tool_name}: {e}")
    
    return tool_results


def merge_results(ground_truth, tool_results, hg19_tools=None):
    """Merge tool results with ground truth"""
    print("\nMerging tool results with ground truth...")
    
    if hg19_tools is None:
        hg19_tools = ['Franklin', 'VIP-HL']
    
    merged = ground_truth.copy()
    
    for tool_name, tool_df in tool_results.items():
        tool_data = tool_df[['Variant_Key', 'Classification', 'ACMG_Criteria']].copy()
        tool_data = tool_data.rename(columns={
            'Classification': f'{tool_name}_Classification',
            'ACMG_Criteria': f'{tool_name}_ACMG_Criteria'
        })
        
        # Tools using hg19 coordinates
        if tool_name in hg19_tools and 'Variant_Key_hg19' in merged.columns:
            tool_data = tool_data.rename(columns={'Variant_Key': 'Variant_Key_hg19'})
            merged = merged.merge(tool_data, on='Variant_Key_hg19', how='left')
        else:
            merged = merged.merge(tool_data, on='Variant_Key', how='left')
        
        matched = merged[f'{tool_name}_Classification'].notna().sum()
        print(f"  Added {tool_name}: {matched} variants matched")
    
    return merged


def main():
    parser = argparse.ArgumentParser(description='Parse and merge tool results')
    parser.add_argument('--ground-truth', required=True, help='Ground truth file (Excel or TSV)')
    parser.add_argument('--results-dir', required=True, help='Directory containing tool results')
    parser.add_argument('--tool-files', required=True, help='JSON string mapping tool names to filenames')
    parser.add_argument('--output', required=True, help='Output merged results TSV')
    parser.add_argument('--dataset-type', default='foxl2', help='Dataset type (foxl2 or clingen)')
    
    args = parser.parse_args()
    
    # Parse tool files mapping
    import json
    tool_files_dict = json.loads(args.tool_files)
    
    # Load ground truth
    ground_truth = load_ground_truth(args.ground_truth, args.dataset_type)
    
    # Parse tool results
    tool_results = parse_tool_results(tool_files_dict, args.results_dir)
    
    # Merge results
    merged_results = merge_results(ground_truth, tool_results)
    
    # Save merged results
    merged_results.to_csv(args.output, sep='\t', index=False)
    print(f"\n✓ Saved merged results to: {args.output}")
    print(f"  Total variants: {len(merged_results)}")
    print(f"  Total columns: {len(merged_results.columns)}")


if __name__ == '__main__':
    main()
