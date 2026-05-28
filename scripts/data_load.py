import pandas as pd

def load_and_filter(sample_size=None):
    df = pd.read_parquet("data/26_29_dataset.parquet")
    if sample_size is not None:
        df = df.sample(sample_size, random_state=42)

    return df