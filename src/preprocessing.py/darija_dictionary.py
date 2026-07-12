
# -*- coding: utf-8 -*-
"""
Dictionnaire de normalisation pour la darija transcrite en alphabet latin
("arabizi"). Objectif : réduire la variance orthographique (plusieurs
graphies pour un même mot) pour aider le modèle à généraliser, SANS tenter
de convertir vers l'écriture arabe (tâche à part entière, hors périmètre ici).

⚠️ Ceci est un dictionnaire DE DÉPART, volontairement modeste (~45 entrées).
Il couvre les variantes les plus fréquentes observées dans l'échantillon
d'exploration (vocabulaire courant + vocabulaire télécom : réseau, offre,
prix, problème...). À enrichir progressivement au fil de l'inspection
manuelle du corpus (phase d'annotation notamment) plutôt que de viser
l'exhaustivité dès maintenant.

Convention : les chiffres utilisés comme lettres (2, 3, 5, 7, 9) sont
volontairement CONSERVÉS tels quels dans les mots (ex. "3lach" reste
"3lach") — les tokenizers DarijaBERT/XLM-R rencontrés en phase 4 les
traitent déjà comme des unités valides. Seules les variantes orthographiques
autour d'un même mot sont uniformisées.

Emplacement : src/preprocessing/darija_dictionary.py
"""

DARIJA_NORMALIZATION_DICT = {
    # Interrogatifs / expressions courantes
    "wach": "wach", "wash": "wach",
    "chno": "chno", "chnoo": "chno", "chnou": "chno", "ch7al": "ch7al", "chhal": "ch7al",
    "3lach": "3lach", "3la9ach": "3lach", "3lah": "3lach",
    "kifach": "kifach", "kif": "kifach",
    "fin": "fin", "finn": "fin",
    "imta": "imta", "imtach": "imta",

    # Quantité / intensité
    "bzz": "bezzaf", "bzzf": "bezzaf", "bezaf": "bezzaf", "bezzef": "bezzaf", "bezzaf": "bezzaf",
    "chwiya": "chwiya", "chwia": "chwiya", "chouiya": "chwiya",
    "ghi": "ghir", "ghire": "ghir", "ghir": "ghir",

    # Qualificatifs fréquents (positif/négatif) — utiles pour le signal de sentiment
    "mzyan": "mezyan", "mezyan": "mezyan", "mezyane": "mezyan", "mzian": "mezyan",
    "khayb": "khayb", "khaib": "khayb", "khayba": "khayb",
    "zwin": "zwin", "zwina": "zwin", "zwine": "zwin",
    "naql": "nul", "null": "nul", "nul": "nul",

    # Présence / absence — très fréquent dans les plaintes réseau
    "kayn": "kayn", "kayen": "kayn", "kayan": "kayn",
    "makaynch": "makaynch", "makainch": "makaynch", "ma kaynch": "makaynch",
    "walo": "walou", "walou": "walou",

    # Négation
    "mafihach": "mafihach", "ma fihach": "mafihach", "mafiha": "mafihach",
    "machi": "machi", "maci": "machi",

    # Vocabulaire télécom fréquent
    "rizo": "reseau", "réso": "reseau", "reso": "reseau",
    "l3ard": "l3ard", "l3ardh": "l3ard", "3ard": "l3ard",  # "l'offre"
    "flouss": "flouss", "flous": "flouss", "floss": "flouss",  # "l'argent"
    "chi haja": "chi_haja", "chihaja": "chi_haja",  # "quelque chose"

    # Salutations / politesse
    "salam": "salam", "slm": "salam", "salamo": "salam",
    "chokran": "choukran", "choukran": "choukran", "shukran": "choukran",
}


def get_dictionary_size() -> int:
    """Nombre d'entrées uniques (clés) dans le dictionnaire."""
    return len(DARIJA_NORMALIZATION_DICT)
