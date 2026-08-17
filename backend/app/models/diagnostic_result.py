"""Modèle de persistance des résultats de diagnostic.

Volontairement : AUCUNE colonne image/photo/blob ici. Ce modèle ne stocke
que le résultat dérivé d'un diagnostic, jamais la donnée source (photo).
Voir docs/CLAUDE.md § Principes de confidentialité des données.

`pillar` et `category` sont pensés pour être extensibles aux 3 autres
piliers du produit (Mental, Organisation, Finances/Carrière), même si
seul "physique" est peuplé en V1.
"""

import datetime
import uuid

from sqlalchemy import JSON, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class DiagnosticResult(Base):
    __tablename__ = "diagnostic_results"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String, index=True)
    pillar: Mapped[str] = mapped_column(String, default="physique")
    category: Mapped[str] = mapped_column(String)  # ex: "colorimetrie" | "morphologie_silhouette"
    payload: Mapped[dict] = mapped_column(JSON)
    rules_version: Mapped[str] = mapped_column(String, default="v0-prototype")
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc)
    )
