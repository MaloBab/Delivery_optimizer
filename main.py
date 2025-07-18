import pandas as pd
from tkinter import Tk, filedialog
from excel_parser import parse_excel
from retard_detector import detect_retards
from optimizer import propose_remplacement, propose_swap
from exporter import export_results
from models import Robot, Besoin
from collections import defaultdict

# Sélection du fichier via boîte de dialogue
Tk().withdraw()
path = filedialog.askopenfilename(
    title="Sélectionner le fichier Excel d'entrée",
    filetypes=[("Excel files", "*.xlsx")]
)
if not path:
    print("Aucun fichier sélectionné. Fin du programme.")
    exit()


column_mapping = {
    "Item Number Requested": "Item Number",
    "Item#": "Item Number",
    "JDE Item# ordered\n(Robot Configuration)": "Item Number",
    "Required Delivery date @Bizlink": "Date Besoin"
}

result = parse_excel(
    path,
    use_dataframe=True,
    expected_sheets=["ANALYSE", "REPORT FEC", "PIPELINE"],
    column_mapping=column_mapping
)
# Détection des retards avec logique centralisée
retards_df = detect_retards(result["ANALYSE"])

# Conversion des besoins à partir des lignes en retard
besoins = []
for _, row in retards_df.iterrows():
    date_besoin = pd.to_datetime(row["Date Besoin"], errors="coerce")
    date_dispo = pd.to_datetime(row["Promised date @CONTERN"], errors="coerce")
    if pd.isna(date_besoin) or pd.isna(date_dispo):
        continue  # Ignore les besoins sans dates valides
    besoins.append(Besoin(
        id=row.get("FPack Number"),
        item_number=row["Item Number"],
        projet=row["E#"],
        date_besoin=date_besoin,
        date_disponibilite=date_dispo,
        delta=row["Delta"]
    ))

stock = []
for _, row in result["REPORT FEC"].iterrows():
    date_dispo = pd.to_datetime(row["Correct RecDate3"], errors="coerce")
    if pd.isna(date_dispo):
        continue
    stock.append(Robot(
        id=row["Lot#"],
        item_number=row["Item Number"],
        model=row.get("Model"),
        date_disponibilite=date_dispo,
        localisation=row.get("Localisation", ""),
        affecte=False
    ))

pipeline = []
for _, row in result["PIPELINE"].iterrows():
    date_dispo = pd.to_datetime(row["Possible date @BIZLINK"], errors="coerce")
    if pd.isna(date_dispo):
        continue
    pipeline.append(Robot(
        id=row["E#"],
        item_number=row["Item Number"],
        model=row.get("Robot type"),
        date_disponibilite=date_dispo,
        localisation=row.get("Localisation", ""),
        affecte=False
    ))

robots_libres = stock + pipeline

remplacements = []
swaps = []
for besoin in besoins:
    remplacement = propose_remplacement(besoin, robots_libres)
    if remplacement:
        remplacements.append({
            "ID Projet": besoin.projet,
            "ITEM": besoin.item_number,
            "Date de dispo initiale": besoin.date_disponibilite,
            "projet de remplacement (Remplacement ID)": remplacement.id,
            "Nouvelle date de dispo": remplacement.date_disponibilite
        })
        remplacement.affecte = True
    else:
        swap = propose_swap(besoin, [b for b in besoins if b.id != besoin.id])
        if swap:
            swaps.append({
                "Projet A": besoin.projet,
                "Projet B": swap.projet,
                "Item": besoin.item_number,
                "Swap A": besoin.id,
                "Swap B": swap.id
            })

revue = []
model_stats = defaultdict(list)
for r in robots_libres:
    model_stats[r.model].append(r)

for model, robots in model_stats.items():
    revue.append({
        "Modèle": model,
        "Robots libres": len(robots),
        "Date la plus proche": min(r.date_disponibilite for r in robots),
        "Max Retard": max((b.delta for b in besoins if b.item_number == robots[0].item_number), default=None)
    })

export_results(remplacements, swaps, revue)
print("Optimisation terminée. Résultat exporté dans 'output.xlsx'.")