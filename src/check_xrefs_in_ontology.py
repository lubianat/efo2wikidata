import pandas as pd
import os

input_file_path = os.path.join("data", "efo_clean.csv")
output_file_path = os.path.join("data", "xref_table.csv")

# Load CSV, skip bad lines
df = pd.read_csv(input_file_path, on_bad_lines='skip')

# Extract xref_prefix and example
def extract_xref(xref):
    if pd.isnull(xref):
        return None, None
    if '|' in xref:
        xref = xref.split('|')[0]
    parts = xref.split(':')
    if len(parts) > 1:
        return parts[0], ':'.join(parts[1:])
    return None, None

df['xref_prefix'], df['example'] = zip(*df['xrefs'].map(extract_xref))

# Filter only unique prefixes
df_unique = df.drop_duplicates(subset='xref_prefix')[['xref_prefix', 'example']]
df_unique.dropna(inplace=True)

# Save to new CSV
df_unique.to_csv(output_file_path, index=False)
