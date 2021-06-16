#!/usr/bin/env python3

import pandas as pd
from Bio import SeqIO


def load_fasta_into_df(fasta_file:str):
    '''Load a fasta file into a pandas data frame.'''
    d = {'id':[], 'description':[], 'sequence':[]}
    
    for record in SeqIO.parse(fasta_file, 'fasta'):
        d['id'].append(record.id)
        d['description'].append(record.description)
        d['sequence'].append(str(record.seq))

    return pd.DataFrame.from_dict(d)

def load_merlin_codebook(codebook_file:str):
    '''Load the MERlin style codebook.'''
    version = ''
    codebook_name = ''
    bit_names = []
    barcode_dict = {'name':[], 'id':[], 'barcode_str':[]}
    
    with open(codebook_file, 'r') as f:
        lines = f.readlines()
        is_header = True
    
        for l in lines:
            sl = l.split(',')
            
            # Skip blank lines
            if len(sl) == 0:
                continue
            
            # Load the header
            if is_header:
                if sl[0].strip() == 'version':
                    version = sl[1].strip()
                elif sl[0].strip() == 'codebook_name':
                    codebook_name = sl[1].strip()
                elif sl[0].strip() == 'bit_names':
                    bit_names = [sl[i].strip() for i in range(1, len(sl))]
                elif sl[0].strip() == 'name':
                    is_header = False
                    continue
                
            # Load the barcode table
            else:
                barcode_dict['name'].append(sl[0].strip())
                barcode_dict['id'].append(sl[1].strip())
                barcode_dict['barcode_str'].append(sl[2].strip())
    
    return version, codebook_name, bit_names, pd.DataFrame.from_dict(barcode_dict)

def load_transcriptome(transcripts_fasta_file:str, fpkm_tracking_file:str):
    '''Load the transcriptome into a pandas data frame.'''
    
    # Load the transcripts
    transcripts = load_fasta_into_df(transcripts_fasta_file)
    print(f'Loaded {transcripts.shape[0]} transcripts.')
    transcripts.rename(columns={'id':'transcript_id'}, inplace=True)
    
    # Load the FPKMs
    fpkms = pd.read_csv(fpkm_tracking_file, sep='\t')
    print(f'Loaded FPKMs for {fpkms.shape[0]} transcripts of {len(pd.unique(fpkms["gene_id"]))} genes.')
    fpkms.rename(columns={'tracking_id':'transcript_id'}, inplace=True)
    
    # Merge the two data frames
    transcriptome = transcripts.merge(fpkms, how='inner', on='transcript_id')
    print(f'Kept {transcriptome.shape[0]} transcripts of {len(pd.unique(transcriptome["gene_id"]))} genes after merging.')
    
    return transcriptome