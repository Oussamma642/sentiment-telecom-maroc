
# -*- coding: utf-8 -*-
"""
Phase 2 - Étape 3 : Détection et documentation du code-switching.

⚠️ Ceci est une classification HEURISTIQUE, pas une détection de langue
certifiée (des outils comme langdetect/fasttext échouent sur la darija,
qui n'est pas une langue "standard" qu'ils reconnaissent). L'objectif n'est
pas d'obtenir un label parfait, mais de pouvoir ensuite croiser la
performance du modèle (phase 4) avec le type de texte rencontré.

Catégories produites (colonne `language_category`) :
    - "arabic"                 : uniquement écriture arabe
    - "mixed_arabic_latin"     : écriture arabe ET alphabet latin dans le même texte
    - "darija_latin"           : alphabet latin, vocabulaire/marqueurs darija détectés
    - "french"                 : alphabet latin, vocabulaire français détecté, pas de marqueur darija
    - "mixed_latin_fr_darija"  : alphabet latin, marqueurs français ET darija (code-switching pur latin)
    - "other_latin"            : alphabet latin sans marqueur clair (ex. "good", "top", noms propres)
    - "symbols_only"           : ni lettre arabe ni lettre latine (emojis, ponctuation seule)

Colonne `is_code_switching` (bool) : True si le texte mélange manifestement
plusieurs systèmes linguistiques (arabe+latin, ou français+darija en latin).

Entrée  : data/interim/corpus_cleaned_step2.csv
Sortie  : data/interim/corpus_cleaned_step3.csv

Emplacement : src/preprocessing/detect_language_mix.py
Exécution   : python -m src.preprocessing.detect_language_mix
              (ou directement : python detect_language_mix.py depuis ce dossier)
"""

import re
import sys
from pathlib import Path

import pandas as pd

try:
    from .darija_dictionary import DARIJA_NORMALIZATION_DICT
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from darija_dictionary import DARIJA_NORMALIZATION_DICT

# Plages Unicode couvrant l'écriture arabe (arabe standard + darija en caractères arabes)
ARABIC_CHAR_PATTERN = re.compile(
    r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]"
)
LATIN_CHAR_PATTERN = re.compile(r"[a-zA-Z]")

# Mot latin contenant un chiffre entouré de lettres = marqueur "arabizi"
# fréquent (ex. "l3ard", "chn9ach", "wa7ed") -> signal fort de darija latinisée
ARABIZI_DIGIT_PATTERN = re.compile(r"[a-zA-Z]+[273905][a-zA-Z]*|[a-zA-Z]*[273905][a-zA-Z]+")

WORD_PATTERN = re.compile(r"[a-zA-Z]+")

# Liste courte de mots français très fréquents, suffisante pour détecter la
# présence de français sans viser l'exhaustivité (stopwords + vocabulaire
# récurrent dans les avis/commentaires télécom)
FRENCH_MARKERS = {
    "le", "la", "les", "de", "des", "du", "un", "une", "et", "est", "pas",
    "avec", "pour", "mais", "ce", "qui", "que", "dans", "sur", "plus", "tres",
    "très", "service", "merci", "bonjour", "bien", "tout", "vous", "votre",
    "nous", "notre", "j'ai", "jai", "cest", "c'est", "il", "elle", "sont",
    "chez", "meme", "même", "encore", "toujours", "jamais", "problème",
    "probleme", "internet", "reseau", "réseau", "offre", "client", "aide",
    "svp", "merci", "bonsoir", "salut", "depuis", "quand", "comment",
}

# Marqueurs darija en latin : on réutilise le dictionnaire de normalisation
# (clés = variantes brutes, valeurs = formes canoniques) comme liste de mots-indices
DARIJA_MARKERS = set(DARIJA_NORMALIZATION_DICT.keys()) | set(DARIJA_NORMALIZATION_DICT.values())


def classify_text(text: str) -> tuple[str, bool]:
    """Retourne (language_category, is_code_switching) pour un texte donné."""
    if not isinstance(text, str) or not text.strip():
        return "symbols_only", False

    has_arabic = bool(ARABIC_CHAR_PATTERN.search(text))
    has_latin = bool(LATIN_CHAR_PATTERN.search(text))

    if has_arabic and has_latin:
        return "mixed_arabic_latin", True
    if has_arabic and not has_latin:
        return "arabic", False
    if not has_arabic and not has_latin:
        return "symbols_only", False

    # À partir d'ici : alphabet latin uniquement (has_latin=True, has_arabic=False)
    tokens = {t.lower() for t in WORD_PATTERN.findall(text)}
    has_arabizi_digit = bool(ARABIZI_DIGIT_PATTERN.search(text))
    darija_hits = len(tokens & DARIJA_MARKERS) + (1 if has_arabizi_digit else 0)
    french_hits = len(tokens & FRENCH_MARKERS)

    if darija_hits > 0 and french_hits > 0:
        return "mixed_latin_fr_darija", True
    if darija_hits > 0:
        return "darija_latin", False
    if french_hits > 0:
        return "french", False
    return "other_latin", False


def main():
    project_root = Path(__file__).resolve().parents[2]
    input_path = project_root / "data" / "interim" / "corpus_cleaned_step2.csv"
    output_path = project_root / "data" / "interim" / "corpus_cleaned_step3.csv"

    df = pd.read_csv(input_path)
    print(f"Corpus chargé : {len(df)} lignes")

    results = df["text"].apply(classify_text)
    df["language_category"] = results.apply(lambda r: r[0])
    df["is_code_switching"] = results.apply(lambda r: r[1])

    print("\n=== Répartition par catégorie linguistique ===")
    print(df["language_category"].value_counts())
    print(f"\nTaux de code-switching détecté : {df['is_code_switching'].mean() * 100:.1f}%")

    print("\n=== Répartition par opérateur ===")
    print(pd.crosstab(df["operator"], df["language_category"]))

    print("\n=== Exemples par catégorie ===")
    for category in df["language_category"].unique():
        sample = df[df["language_category"] == category].sample(
            min(2, (df["language_category"] == category).sum()), random_state=42
        )
        print(f"\n[{category}]")
        for _, row in sample.iterrows():
            print(f"  - {row['text'][:100]}")

    df.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"\n→ Sauvegardé : {output_path}")


if __name__ == "__main__":
    main()
