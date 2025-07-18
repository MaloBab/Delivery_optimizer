def propose_remplacement(besoin, robots_libres, max_retard_tolere=3):
    """
    Propose le robot libre le plus adapté :
    - Priorité à ceux disponibles avant la date de besoin.
    - Sinon, tolère un léger retard (max_retard_tolere jours).
    - Prend le robot le plus proche de la date de besoin.
    """
    candidats = []
    for r in robots_libres:
        if r.item_number != besoin.item_number or getattr(r, "affecte", False):
            continue
        retard = (r.date_disponibilite - besoin.date_besoin).days
        if retard <= 0:
            candidats.append((abs(retard), r))  # parfait ou en avance
        elif retard <= max_retard_tolere:
            candidats.append((retard + 1000, r))  # léger retard, pénalisé mais accepté
    if not candidats:
        return None
    # Trie par priorité (avance/retard le plus faible)
    return sorted(candidats, key=lambda x: x[0])[0][1]

def propose_swap(besoin_retarde, autres_besoins):
    """
    Propose un swap qui réduit le retard global :
    - Cherche un besoin avec le même item_number.
    - Le swap ne doit pas aggraver le retard de l'autre besoin.
    - Privilégie le swap qui réduit le plus le retard total.
    """
    best_swap = None
    best_gain = 0
    for autre in autres_besoins:
        if autre.item_number != besoin_retarde.item_number or autre.id == besoin_retarde.id:
            continue
        # Si on échange les dates de dispo
        retard_avant = max(0, (besoin_retarde.date_disponibilite - besoin_retarde.date_besoin).days) \
                     + max(0, (autre.date_disponibilite - autre.date_besoin).days)
        retard_apres = max(0, (autre.date_disponibilite - besoin_retarde.date_besoin).days) \
                     + max(0, (besoin_retarde.date_disponibilite - autre.date_besoin).days)
        gain = retard_avant - retard_apres
        # On ne propose que si le swap améliore la situation globale
        if gain > best_gain and (autre.date_disponibilite <= besoin_retarde.date_besoin or besoin_retarde.date_disponibilite <= autre.date_besoin):
            best_gain = gain
            best_swap = autre
    return best_swap