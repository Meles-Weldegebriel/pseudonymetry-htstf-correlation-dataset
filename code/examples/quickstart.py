import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('data/dataset.csv')

print(df.head())
print(df.describe())

if 'pnr' in df.columns:
    df['pnr'].dropna().hist(bins=40)
    plt.title('Distribution of PNR')
    plt.xlabel('PNR')
    plt.ylabel('Count')
    plt.show()
