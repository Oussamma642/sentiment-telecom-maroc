
# -*- coding: utf-8 -*-
"""
Phase 2 - Étape 4 : Comparaison des tokenizers DarijaBERT-mix vs XLM-RoBERTa.

Objectif : anticiper, avant la phase 4 (fine-tuning), comment chaque
tokenizer segmente les textes réellement présents dans le corpus — en
particulier les catégories à fort enjeu (darija latinisée, code-switching
arabe/latin). Un tokenizer qui fragmente excessivement un mot en plusieurs
sous-tokens perd en général en qualité de représentation.

Modèles comparés :
    - SI2M-Lab/DarijaBERT-mix : variante DarijaBERT entraînée pour gérer
      à la fois l'écriture arabe ET la darija latinisée (arabizi) — choix
      le plus cohérent avec ce corpus qui mélange les deux écritures.
    - xlm-roberta-base : modèle multilingue généraliste, référence de
      comparaison.

Métrique principale : le ratio (nombre de sous-tokens / nombre de mots),
calculé par catégorie linguistique (language_category, issue de l'étape 3).
Un ratio proche de 1 signifie que le tokenizer reconnaît la plupart des
mots comme des unités entières ; un ratio élevé signifie une fragmentation
importante (moins bon signe pour ce type de texte).

Entrée  : data/interim/corpus_cleaned_step3.csv
Sortie  : reports/tokenizer_comparison.csv + affichage détaillé en console

Dépendances : pip install transformers sentencepiece
Emplacement : src/preprocessing/compare_tokenizers.py
Exécution   : python -m src.preprocessing.compare_tokenizers
              (ou directement : python compare_tokenizers.py depuis ce dossier)

⚠️ Nécessite un accès internet à huggingface.co pour télécharger les
tokenizers au premier lancement (téléchargement mis en cache ensuite).
"""

import re
import sys
from pathlib import Path

import pandas as pd
from transformers import AutoTokenizer

MODELS = {
    "DarijaBERT-mix": "SI2M-Lab/DarijaBERT-mix",
    "XLM-RoBERTa": "xlm-roberta-base",
}

SAMPLES_PER_CATEGORY = 30  # nombre de textes échantillonnés par catégorie pour la mesure
WORD_PATTERN = re.compile(r"\S+")  # découpage simple par espaces pour compter les "mots" de référence


def load_tokenizers() -> dict:
    tokenizers = {}
    for name, checkpoint in MODELS.items():
        print(f"Chargement du tokenizer {name} ({checkpoint})...")
        tokenizers[name] = AutoTokenizer.from_pretrained(checkpoint)
    return tokenizers


def fragmentation_ratio(text: str, tokenizer) -> float:
    """Ratio (nb sous-tokens produits par le tokenizer) / (nb mots bruts).
    On exclut les tokens spéciaux ([CLS], [SEP], <s>, etc.) du compte."""
    n_words = len(WORD_PATTERN.findall(text))
    if n_words == 0:
        return None

    tokens = tokenizer.tokenize(text)
    return len(tokens) / n_words


def compare_on_sample(df: pd.DataFrame, tokenizers: dict) -> pd.DataFrame:
    results = []

    for category in df["language_category"].unique():
        subset = df[df["language_category"] == category]
        sample = subset.sample(min(SAMPLES_PER_CATEGORY, len(subset)), random_state=42)

        for name, tokenizer in tokenizers.items():
            ratios = [
                r for r in (fragmentation_ratio(t, tokenizer) for t in sample["text"])
                if r is not None
            ]
            if ratios:
                results.append({
                    "language_category": category,
                    "tokenizer": name,
                    "n_samples": len(ratios),
                    "avg_subtokens_per_word": sum(ratios) / len(ratios),
                })

    return pd.DataFrame(results)


def show_examples(df: pd.DataFrame, tokenizers: dict, n_examples: int = 3) -> None:
    """Affiche la segmentation concrète de quelques exemples représentatifs,
    en priorité les catégories de code-switching (le vrai enjeu du projet)."""
    priority_categories = ["mixed_arabic_latin", "mixed_latin_fr_darija", "darija_latin"]
    examples = df[df["language_category"].isin(priority_categories)].sample(
        min(n_examples, len(df[df["language_category"].isin(priority_categories)])),
        random_state=42
    )

    print("\n=== Exemples de segmentation (catégories de code-switching) ===")
    for _, row in examples.iterrows():
        print(f"\n[{row['language_category']}] {row['text'][:120]}")
        for name, tokenizer in tokenizers.items():
            tokens = tokenizer.tokenize(row["text"])
            print(f"  {name} ({len(tokens)} sous-tokens) : {tokens}")


def main():
    project_root = Path(__file__).resolve().parents[2]
    input_path = project_root / "data" / "interim" / "corpus_cleaned_step3.csv"
    output_path = project_root / "reports" / "tokenizer_comparison.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(input_path)
    print(f"Corpus chargé : {len(df)} lignes\n")

    tokenizers = load_tokenizers()

    print(f"\nComparaison sur un échantillon de {SAMPLES_PER_CATEGORY} textes par catégorie...")
    results = compare_on_sample(df, tokenizers)

    pivot = results.pivot(index="language_category", columns="tokenizer",
                           values="avg_subtokens_per_word").round(2)
    print("\n=== Fragmentation moyenne (sous-tokens par mot) ===")
    print(pivot)
    print("\nUn chiffre plus proche de 1.0 = meilleure reconnaissance du vocabulaire par le tokenizer.")

    show_examples(df, tokenizers)

    results.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"\n→ Résultats sauvegardés : {output_path}")


if __name__ == "__main__":
    main()
