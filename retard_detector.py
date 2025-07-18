import pandas as pd
import numpy as np

def deduplicate_columns(columns):
    seen = {}
    new_columns = []
    for col in columns:
        col_str = str(col).strip()
        if col_str in seen:
            seen[col_str] += 1
            new_columns.append(f"{col_str}_{seen[col_str]}")
        else:
            seen[col_str] = 0
            new_columns.append(col_str)
    return new_columns

def detect_retards(df):
    col_delta = None
    for col in df.columns:
        if str(col).strip().lower() == "delta":
            col_delta = col
            break
    if col_delta is None:
        print("[WARN] Aucune colonne 'Delta' trouvée.")
        return pd.DataFrame()

    df_dedup = df.copy()
    deduped_columns = deduplicate_columns(df.columns)
    df_dedup.columns = deduped_columns

    for col in deduped_columns:
        if col.lower() == "delta":
            dedup_col_delta = col
            break

    df_dedup["Retard détecté"] = df_dedup[dedup_col_delta].apply(
        lambda x: isinstance(x, (int, float)) and x < 0
    )
    return df_dedup[df_dedup["Retard détecté"]]
