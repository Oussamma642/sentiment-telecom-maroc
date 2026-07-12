# -*- coding: utf-8 -*-
"""
Phase 2 - Étape 2 : Normalisation de la darija transcrite en alphabet latin.

Deux traitements appliqués, uniquement sur les tokens en alphabet latin
(le texte en écriture arabe n'est pas touché) :
    1. Réduction des élongations ("bzzzzzf" -> "bzzf", "heeey" -> "heey")
       -> traitement générique, à faible risque, utile pour toutes les langues
    2. Application du dictionnaire de normalisation darija (voir
       darija_dictionary.py) -> traitement ciblé sur les variantes connues

Entrée  : data/interim/corpus_cleaned_step1.csv
Sortie  : data/interim/corpus_cleaned_step2.csv

Emplacement : src/preprocessing/normalize_darija.py
Exécution   : python -m src.preprocessing.normalize_darija
"""

import re
import sys
from pathlib import Path

import pandas as pd

try:
    from .darija_dictionary import DARIJA_NORMALIZATION_DICT, get_dictionary_size
except ImportError:
    # Le script a été lancé directement (ex. clic "Run" dans l'éditeur, ou
    # `python normalize_darija.py`) plutôt que via `python -m src.preprocessing...`
    # depuis la racine du projet. On ajoute le dossier courant au chemin de
    # recherche des modules pour que l'import fonctionne quand même.
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from darija_dictionary import DARIJA_NORMALIZATION_DICT, get_dictionary_size

# Détecte un caractère répété 3 fois ou plus (lettres latines uniquement,
# on laisse l'arabe et les emojis intacts)
ELONGATION_PATTERN = re.compile(r"([a-zA-Z])\1{2,}")

# Un "mot" latin = suite de lettres/chiffres, pour repérer les tokens à normaliser
# sans casser les mots en écriture arabe ou les emojis
LATIN_TOKEN_PATTERN = re.compile(r"[a-zA-Z0-9]+")


def reduce_elongation(text: str) -> str:
    """Réduit toute lettre latine répétée 3+ fois à 2 occurrences."""
    return ELONGATION_PATTERN.sub(r"\1\1", text)


def normalize_darija_tokens(text: str) -> str:
    """Remplace chaque token latin trouvé dans le dictionnaire par sa forme canonique.
    Insensible à la casse ; le reste du texte (arabe, emojis, ponctuation) n'est pas touché."""

    def replace_token(match: re.Match) -> str:
        token = match.group(0)
        canonical = DARIJA_NORMALIZATION_DICT.get(token.lower())
        return canonical if canonical else token

    return LATIN_TOKEN_PATTERN.sub(replace_token, text)


def normalize_text(text: str) -> str:
    if not isinstance(text, str) or not text:
        return text
    text = reduce_elongation(text)
    text = normalize_darija_tokens(text)
    return text


def main():
    project_root = Path(__file__).resolve().parents[2]
    input_path = project_root / "data" / "interim" / "corpus_cleaned_step1.csv"
    output_path = project_root / "data" / "interim" / "corpus_cleaned_step2.csv"

    df = pd.read_csv(input_path)
    print(f"Corpus chargé : {len(df)} lignes")
    print(f"Dictionnaire darija : {get_dictionary_size()} entrées")

    df["text_before_normalization"] = df["text"]
    df["text"] = df["text"].apply(normalize_text)

    n_changed = (df["text"] != df["text_before_normalization"]).sum()
    print(f"\nLignes modifiées par la normalisation : {n_changed} "
          f"({n_changed / len(df) * 100:.1f}%)")

    print("\n=== Exemples de transformations (échantillon) ===")
    changed = df[df["text"] != df["text_before_normalization"]]
    for _, row in changed.sample(min(8, len(changed)), random_state=42).iterrows():
        print(f"  AVANT : {row['text_before_normalization']}")
        print(f"  APRÈS : {row['text']}")
        print("  " + "-" * 60)

    # La colonne de comparaison ne sert qu'au contrôle qualité ci-dessus,
    # on ne la garde pas dans le fichier de sortie
    df = df.drop(columns=["text_before_normalization"])

    df.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"\n→ Sauvegardé : {output_path}")


if __name__ == "__main__":
    main()