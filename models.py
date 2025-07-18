from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Robot:
    id: str
    item_number: str
    model: str
    date_disponibilite: datetime
    localisation: str
    affecte: bool
    projet: Optional[str] = None

@dataclass
class Besoin:
    id: str
    item_number: str
    projet: str
    date_besoin: datetime
    date_disponibilite: datetime
    delta: int  # en jours
