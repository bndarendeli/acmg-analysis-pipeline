from .base_parser import BaseParser
import pandas as pd

class VIPHLParser(BaseParser):
    """Parser for VIP-HL TSV output"""
    
    def __init__(self, tool_name: str = "VIP-HL"):
        super().__init__(tool_name)
    
    def parse(self, file_path: str) -> pd.DataFrame:
        """Parse VIP-HL TSV file"""
        try:
            df = pd.read_csv(file_path, sep='\t', low_memory=False)
            
            if 'Variant_Input' not in df.columns:
                print(f"Error: Variant_Input column not found in VIP-HL file")
                return pd.DataFrame()
            
            results = []
            for idx, row in df.iterrows():
                try:
                    # Parse variant input format: Chr-Pos-Ref-Alt
                    variant_input = str(row['Variant_Input'])
                    parts = variant_input.split('-')
                    if len(parts) != 4:
                        continue
                    
                    chrom = parts[0].replace('chr', '')
                    pos = int(parts[1])
                    ref = parts[2]
                    alt = parts[3]
                    
                    classification = None
                    if 'Classification' in row and pd.notna(row['Classification']):
                        classification = str(row['Classification'])
                    
                    acmg_criteria = []
                    if 'Criteria' in row and pd.notna(row['Criteria']):
                        criteria = str(row['Criteria'])
                        if criteria != '-' and criteria != '.':
                            acmg_criteria = [c.strip() for c in criteria.split(',') if c.strip()]
                    
                    variant_key = self.make_variant_key(chrom, pos, ref, alt)
                    
                    results.append({
                        'Chr': chrom,
                        'Pos': pos,
                        'Ref': ref,
                        'Alt': alt,
                        'Variant_Key': variant_key,
                        'Classification': self.standardize_classification(classification) if classification else None,
                        'ACMG_Criteria': ','.join(acmg_criteria) if acmg_criteria else None,
                        'Tool': self.tool_name
                    })
                except Exception as e:
                    continue
            
            return pd.DataFrame(results)
            
        except Exception as e:
            print(f"Error parsing VIP-HL file {file_path}: {e}")
            return pd.DataFrame()
