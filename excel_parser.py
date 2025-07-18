import pandas as pd
import numpy as np

def clean_header(header_row):
    return [str(h).strip().replace('\n', ' ') if pd.notna(h) else None for h in header_row]

def detect_header(df):
    for i, row in df.iterrows():
        non_empty_indices = row.first_valid_index(), row.last_valid_index()
        if non_empty_indices[0] is None:
            continue
        values = row.tolist()
        start = row.first_valid_index()
        end = None
        for j in range(start, len(values)):
            if pd.isna(values[j]):
                end = j
                break
        if end is None:
            end = len(values)
        if all(pd.isna(v) for v in values[end:]):
            return i, values[start:end]
    return None, []

def parse_excel(path, use_dataframe=True, expected_sheets=None):
    xl = pd.read_excel(path, sheet_name=None, dtype=object, header=None)
    result = {}
    for sheet_name, df in xl.items():
        if expected_sheets and sheet_name.strip().upper() not in expected_sheets:
            continue
        header_row_idx, headers = detect_header(df)
        if not headers:
            print(f"[WARN] Aucun header valide détecté dans la feuille '{sheet_name}'")
            continue
        df_data = df.iloc[header_row_idx + 1:].copy()
        df_data = df_data.iloc[:, :len(headers)]
        df_data.columns = headers
        df_data = df_data.replace({np.nan: None})
        result[sheet_name] = df_data.reset_index(drop=True) if use_dataframe else df_data.to_dict(orient="records")
    return result