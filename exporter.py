import pandas as pd

def export_results(remplacements, swaps, revue, output_path="output.xlsx"):
    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        df_aff = pd.DataFrame(remplacements + swaps)
        df_aff.to_excel(writer, sheet_name="Affectations optimisées", index=False)
        df_revue = pd.DataFrame(revue)
        df_revue.to_excel(writer, sheet_name="Vue informative", index=False)
        print(f"[INFO] Résultats exportés vers {output_path}")
