def propose_remplacement(besoin, robots_libres):
    compatibles = [r for r in robots_libres if r.item_number == besoin.item_number and r.date_disponibilite <= besoin.date_besoin]
    if compatibles:
        return sorted(compatibles, key=lambda r: r.date_disponibilite)[0]
    return None

def propose_swap(besoin_retarde, autres_besoins):
    swaps_possibles = []
    for autre in autres_besoins:
        if autre.item_number != besoin_retarde.item_number:
            continue
        if autre.date_disponibilite < besoin_retarde.date_disponibilite and autre.date_besoin >= besoin_retarde.date_disponibilite:
            swaps_possibles.append(autre)
    if swaps_possibles:
        return sorted(swaps_possibles, key=lambda x: x.date_disponibilite)[0]
    return None