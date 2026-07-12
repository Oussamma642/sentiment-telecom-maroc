
# -*- coding: utf-8 -*-
"""
Phase 2 - Étape 1 : Nettoyage textuel de base du corpus consolidé.

Ce script ne touche PAS encore à la darija latinisée (étape 2) ni à la
détection de langue (étape 3) — il se limite à retirer le "bruit" technique
qui n'apporte aucune information pour l'analyse de sentiment :
    - URLs
    - caractères de contrôle / caractères invisibles (zero-width)
    - espaces et sauts de ligne redondants
    - normalisation Unicode (formes multiples du même caractère arabe/latin)
    - lignes devenues vides après nettoyage
    - doublons stricts accidentels (même source + même id)

Entrée  : data/interim/corpus_combined_raw.csv
Sortie  : data/interim/corpus_cleaned_step1.csv

Toujours dans interim/ : la normalisation darija et la détection de langue
(étapes 2 et 3) restent à faire avant que le corpus soit "processed".

Emplacement : src/preprocessing/clean_text_corpus.py
Exécution   : python -m src.preprocessing.clean_text_corpus
"""

import re
import unicodedata
from pathlib import Path

import pandas as pd

# Emojis courants à préserver : ils portent un signal de sentiment fort en darija
# ("😍😍😍" est un commentaire à part entière). On ne les supprime jamais ici.

URL_PATTERN = re.compile(r"https?://\S+|www\.\S+")
# Caractères de contrôle et de largeur nulle (souvent invisibles, issus de copier-coller)
ZERO_WIDTH_PATTERN = re.compile(r"[\u200b\u200c\u200d\u200e\u200f\ufeff]")
WHITESPACE_PATTERN = re.compile(r"\s+")


def normalize_unicode(text: str) -> str:
    """Uniformise les différentes représentations Unicode d'un même caractère
    (ex. certaines lettres arabes ont plusieurs formes équivalentes selon la source)."""
    return unicodedata.normalize("NFKC", text)


def clean_text(text: str) -> str:
    if not isinstance(text, str):
        return ""

    text = normalize_unicode(text)
    text = URL_PATTERN.sub(" ", text)
    text = ZERO_WIDTH_PATTERN.sub("", text)
    text = WHITESPACE_PATTERN.sub(" ", text)
    text = text.strip()

    return text


def clean_corpus(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n_start = len(df)

    df["text"] = df["text"].apply(clean_text)

    # Lignes devenues vides après nettoyage (ex. commentaire qui n'était qu'une URL)
    n_before_empty = len(df)
    df = df[df["text"].str.len() > 0]
    n_after_empty = len(df)
    print(f"  Textes vides après nettoyage retirés : {n_before_empty - n_after_empty}")

    # Doublons stricts accidentels (même source + même identifiant natif)
    n_before_dup = len(df)
    df = df.drop_duplicates(subset=["source", "id"])
    n_after_dup = len(df)
    print(f"  Doublons stricts (source+id) retirés : {n_before_dup - n_after_dup}")

    print(f"\n  Total : {n_start} -> {len(df)} lignes "
          f"({n_start - len(df)} retirées, {(n_start - len(df)) / n_start * 100:.1f}%)")

    return df.reset_index(drop=True)


def main():
    project_root = Path(__file__).resolve().parents[2]
    input_path = project_root / "data" / "interim" / "corpus_combined_raw.csv"
    output_path = project_root / "data" / "interim" / "corpus_cleaned_step1.csv"

    df = pd.read_csv(input_path)
    print(f"Corpus chargé : {len(df)} lignes")

    cleaned = clean_corpus(df)

    cleaned.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"\n→ Sauvegardé : {output_path}")
    print(cleaned.groupby(["operator", "source"]).size())


if __name__ == "__main__":
    main()
