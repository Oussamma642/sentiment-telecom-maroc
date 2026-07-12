# -*- coding: utf-8 -*-
"""
Collecte des commentaires publics sur les publications Facebook des pages
officielles des 3 opérateurs télécoms marocains, via l'API Graph officielle.

Champs collectés : texte, date, + métadonnées (post associé, nb de likes).

PRÉREQUIS (à faire une seule fois, avant d'exécuter ce script) :
1. Créer une app sur https://developers.facebook.com/apps
2. Dans les paramètres de l'app, demander la fonctionnalité
   "Page Public Content Access" (Outils > App Review > Autorisations et fonctionnalités)
3. Soumettre l'app à App Review avec une vidéo de démonstration du cas d'usage
   (analyse de sentiment académique) — validation par Meta requise, non garantie
4. Une fois approuvé, générer un token via l'Explorateur Graph API
   (https://developers.facebook.com/tools/explorer) et le placer dans la variable
   d'environnement FB_ACCESS_TOKEN (ne JAMAIS committer un token dans le code)

Emplacement : src/scraping/facebook_scraper.py
Dépendance  : pip install requests
Exécution   : export FB_ACCESS_TOKEN="ton_token"
              python -m src.scraping.facebook_scraper   (depuis la racine du projet)
"""

import csv
import os
import time
from datetime import datetime
from pathlib import Path

import requests

from config import FACEBOOK_PAGES, GRAPH_API_VERSION, FACEBOOK_RAW_OUTPUT_DIR

GRAPH_BASE_URL = f"https://graph.facebook.com/{GRAPH_API_VERSION}"

MAX_POSTS_PER_PAGE = 100        # nombre de publications à parcourir par page
MAX_COMMENTS_PER_POST = 200     # limite de commentaires récupérés par publication
REQUEST_PAUSE_SECONDS = 1       # pause polie entre appels pour respecter le rate limit


def get_access_token() -> str:
    token = os.environ.get("FB_ACCESS_TOKEN")
    if not token:
        raise EnvironmentError(
            "Variable d'environnement FB_ACCESS_TOKEN manquante. "
            "Génère un token via l'Explorateur Graph API et exporte-le avant de lancer ce script."
        )
    return token


def fetch_page_posts(page_username: str, token: str, max_posts: int) -> list[dict]:
    """Récupère les identifiants et dates des publications récentes d'une page."""
    posts = []
    url = f"{GRAPH_BASE_URL}/{page_username}/posts"
    params = {
        "fields": "id,created_time,message",
        "limit": 50,
        "access_token": token,
    }

    while url and len(posts) < max_posts:
        response = requests.get(url, params=params if "?" not in url else None)
        data = response.json()

        if "error" in data:
            print(f"  Erreur API pour {page_username} : {data['error'].get('message')}")
            break

        posts.extend(data.get("data", []))

        # Pagination : l'API renvoie une URL complète prête à l'emploi
        next_url = data.get("paging", {}).get("next")
        url = next_url
        params = None  # déjà inclus dans next_url

        time.sleep(REQUEST_PAUSE_SECONDS)

    return posts[:max_posts]


def fetch_comments_for_post(post_id: str, token: str, max_comments: int) -> list[dict]:
    """Récupère les commentaires publics d'une publication donnée."""
    comments = []
    url = f"{GRAPH_BASE_URL}/{post_id}/comments"
    params = {
        "fields": "id,message,created_time,like_count",
        "limit": 100,
        "access_token": token,
    }

    while url and len(comments) < max_comments:
        response = requests.get(url, params=params if "?" not in url else None)
        data = response.json()

        if "error" in data:
            print(f"  Erreur API sur les commentaires du post {post_id} : {data['error'].get('message')}")
            break

        comments.extend(data.get("data", []))

        next_url = data.get("paging", {}).get("next")
        url = next_url
        params = None

        time.sleep(REQUEST_PAUSE_SECONDS)

    return comments[:max_comments]


def collect_operator_comments(operator_key: str, page_username: str, token: str) -> list[dict]:
    print(f"\nCollecte en cours : page Facebook '{page_username}' ({operator_key})")
    posts = fetch_page_posts(page_username, token, MAX_POSTS_PER_PAGE)
    print(f"  {len(posts)} publications récupérées")

    rows = []
    for post in posts:
        post_id = post.get("id")
        comments = fetch_comments_for_post(post_id, token, MAX_COMMENTS_PER_POST)

        for c in comments:
            rows.append({
                "operator": operator_key,
                "post_id": post_id,
                "comment_id": c.get("id"),
                "text": c.get("message"),
                "date": c.get("created_time"),
                "like_count": c.get("like_count"),
            })

        if comments:
            print(f"    Post {post_id} : {len(comments)} commentaires")

    return rows


def save_to_csv(rows: list[dict], filepath: Path) -> None:
    filepath.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["operator", "post_id", "comment_id", "text", "date", "like_count"]

    with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"  → Sauvegardé : {filepath} ({len(rows)} lignes)")


def main():
    token = get_access_token()
    project_root = Path(__file__).resolve().parents[2]
    output_dir = project_root / FACEBOOK_RAW_OUTPUT_DIR
    run_date = datetime.now().strftime("%Y%m%d")

    all_rows = []

    for operator_key, page_username in FACEBOOK_PAGES.items():
        rows = collect_operator_comments(operator_key, page_username, token)
        all_rows.extend(rows)

        operator_file = output_dir / f"{operator_key}_{run_date}.csv"
        save_to_csv(rows, operator_file)

    combined_file = output_dir / f"facebook_all_operators_{run_date}.csv"
    save_to_csv(all_rows, combined_file)

    print(f"\nTerminé. Total : {len(all_rows)} commentaires collectés pour {len(FACEBOOK_PAGES)} opérateurs.")


if __name__ == "__main__":
    main()