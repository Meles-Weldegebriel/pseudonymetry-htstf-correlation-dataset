import pandas as pd

FEATURE_COLUMNS = [
    'peak','psr','pnr','ratio_peak_to_median','periodic_sum','fwhm',
    'w_peak_period','w_mean_period','w_std_period','w_energy_period','sharpness_period',
    'w_peak_preamble','w_mean_preamble','w_std_preamble','w_energy_preamble','sharpness_preamble'
]

def load_dataset(path='data/dataset.csv'):
    """Load dataset and return (X, y)."""
    df = pd.read_csv(path)
    X = df[FEATURE_COLUMNS]
    y = df['label']
    return X, y

if __name__ == '__main__':
    X, y = load_dataset()
    print(f"Loaded {len(X)} samples with {X.shape[1]} features. Positives: {int(y.sum())}")
