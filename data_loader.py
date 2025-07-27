import pandas as pd

def load_mutation_data(file_path="data/data_mutations.txt"):
    df = pd.read_csv(file_path, sep="\t", comment='#')
    return df

def get_top_mutated_genes(df, top_n=10):
    return df['Hugo_Symbol'].value_counts().head(top_n)
