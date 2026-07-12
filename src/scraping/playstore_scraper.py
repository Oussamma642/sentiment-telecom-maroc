# -*- coding: utf-8 -*-
"""
Scraping des avis Google Play Store pour les applications officielles
des 3 opérateurs télécoms marocains (Maroc Telecom, Orange, inwi).

Champs collectés : note, texte, date (+ métadonnées utiles pour la suite
du pipeline : opérateur, id de l'avis, nombre de "j'aime").

Emplacement : src/scraping/google_play_scraper.py
Dépendance  : pip install google-play-scraper
Exécution   : python -m src.scraping.google_play_scraper   (depuis la racine du projet)
"""

import csv
import time
from datetime import datetime
from pathlib import Path

from google_play_scraper import Sort, reviews

from config import GOOGLE_PLAY_APPS, LANG, COUNTRY, SORT_ORDER, RAW_OUTPUT_DIR

# Nombre max d'avis à récupérer par application.
# Google Play ne garantit pas ce volume : au-delà d'un certain point,
# l'API ne renvoie plus rien de nouveau, ce qui est normal.
MAX_REVIEWS_PER_APP = 5000

# Taille de page interne à l'API (valeur recommandée par la librairie)
BATCH_SIZE = 200

SORT_MAP = {
    "newest": Sort.NEWEST,
    "most_relevant": Sort.MOST_RELEVANT,
}


def scrape_app_reviews(operator_key: str, app_id: str, max_reviews: int) -> list[dict]:
    """
    Récupère les avis d'une application donnée, avec pagination automatique
    via le paramètre continuation_token renvoyé par l'API.
    """
    collected = []
    continuation_token = None

    while len(collected) < max_reviews:
        remaining = max_reviews - len(collected)
        batch_count = min(BATCH_SIZE, remaining)

        result, continuation_token = reviews(
            app_id,
            lang=LANG,
            country=COUNTRY,
            sort=SORT_MAP[SORT_ORDER],
            count=batch_count,
            continuation_token=continuation_token,
        )

        if not result:
            # Plus aucun avis disponible pour cette combinaison lang/country
            break

        for r in result:
            collected.append({
                "operator": operator_key,
                "review_id": r.get("reviewId"),
                "rating": r.get("score"),
                "text": r.get("content"),
                "date": r.get("at").strftime("%Y-%m-%d %H:%M:%S") if r.get("at") else None,
                "thumbs_up": r.get("thumbsUpCount"),
                "app_version": r.get("reviewCreatedVersion"),
            })

        print(f"  [{operator_key}] {len(collected)} avis collectés...")

        if continuation_token is None or continuation_token.token is None:
            # L'API indique qu'il n'y a plus de pages suivantes
            break

        time.sleep(1)  # pause polie pour ne pas solliciter l'API trop vite

    return collected


def save_to_csv(rows: list[dict], filepath: Path) -> None:
    filepath.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["operator", "review_id", "rating", "text", "date", "thumbs_up", "app_version"]

    with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"  → Sauvegardé : {filepath} ({len(rows)} lignes)")


def main():
    project_root = Path(__file__).resolve().parents[2]
    output_dir = project_root / RAW_OUTPUT_DIR
    run_date = datetime.now().strftime("%Y%m%d")

    all_rows = []

    for operator_key, app_info in GOOGLE_PLAY_APPS.items():
        print(f"\nCollecte en cours : {app_info['app_name']} ({operator_key})")
        rows = scrape_app_reviews(operator_key, app_info["app_id"], MAX_REVIEWS_PER_APP)
        all_rows.extend(rows)

        # Un fichier par opérateur (plus simple à inspecter/déboguer)
        operator_file = output_dir / f"{operator_key}_{run_date}.csv"
        save_to_csv(rows, operator_file)

    # Un fichier consolidé pour la suite du pipeline (phase 2 : nettoyage)
    combined_file = output_dir / f"google_play_all_operators_{run_date}.csv"
    save_to_csv(all_rows, combined_file)

    print(f"\nTerminé. Total : {len(all_rows)} avis collectés pour {len(GOOGLE_PLAY_APPS)} opérateurs.")


if __name__ == "__main__":
    main()