import pandas as pd
import numpy as np
from excel_parser import parse_excel
from retard_detector import detect_retards
from optimizer import propose_remplacement, propose_swap
from exporter import export_results
from models import Robot, Besoin
from datetime import datetime

# Charger les fichiers
path = "documents/Analyse_20250707_ST_2.xlsx"
result = parse_excel(path, use_dataframe=True, expected_sheets=["ANALYSE", "REPORT FEC", "PIPELINE"])

# Détection des retards avec logique centralisée
retards_df = detect_retards(result["ANALYSE"])

# Conversion des besoins à partir des lignes en retard
besoins = []
for _, row in retards_df.iterrows():
    besoins.append(Besoin(
        id=row.get("ID") or str(row.name),
        item_number=row["Item Number"],
        projet=row["Projet"],
        date_besoin=pd.to_datetime(row["Date Besoin"]),
        date_disponibilite=pd.to_datetime(row["Date @Bizlink"]),
        delta=row["Delta"]
    ))

stock = []
for _, row in result["REPORT FEC"].iterrows():
    stock.append(Robot(
        id=row["ID"],
        item_number=row["Item Number"],
        model=row.get("Modèle"),
        date_disponibilite=pd.to_datetime(row["Date @Bizlink"]),
        localisation=row.get("Localisation", ""),
        affecte=False
    ))

pipeline = []
for _, row in result["PIPELINE"].iterrows():
    pipeline.append(Robot(
        id=row["ID"],
        item_number=row["Item Number"],
        model=row.get("Modèle"),
        date_disponibilite=pd.to_datetime(row["Date @Bizlink"]),
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
            "Projet": besoin.projet,
            "Item": besoin.item_number,
            "Date besoin": besoin.date_besoin,
            "Remplacement ID": remplacement.id,
            "Date dispo": remplacement.date_disponibilite
        })
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
from collections import defaultdict
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
