# -*- coding: utf-8 -*-
"""
Configuration centrale du projet : identifiants des applications Google Play
des trois opérateurs télécoms marocains ciblés.

Emplacement : src/scraping/config.py
"""

# Identifiants (package name) des applications officielles sur le Google Play Store.
# Vérifiés manuellement sur play.google.com avant utilisation — à recontrôler
# périodiquement, un opérateur peut changer d'app ou en publier une nouvelle.
GOOGLE_PLAY_APPS = {
    "maroc_telecom": {
        "app_id": "com.MT.selfCare",
        "app_name": "Mon Espace MT",
    },
    "orange": {
        "app_id": "com.orange.meditel.mediteletmoi",
        "app_name": "Orange et moi Maroc",
    },
    "inwi": {
        "app_id": "ma.inwi.selfcaremobile",
        "app_name": "My inwi",
    },
}

# Paramètres de scraping
LANG = "fr"          # langue demandée à l'API (n'empêche pas la darija/arabe dans les avis)
COUNTRY = "ma"        # store marocain
SORT_ORDER = "newest"  # on trie par récence pour prioriser les avis actuels

# Chemin de sortie des données brutes (relatif à la racine du projet)
RAW_OUTPUT_DIR = "data/raw/google_play"

# ---------------------------------------------------------------------------
# Facebook (Graph API)
# ---------------------------------------------------------------------------

# Pages Facebook officielles des 3 opérateurs (noms d'utilisateur publics,
# utilisés comme identifiants dans les appels Graph API : /{page_username}/posts)
FACEBOOK_PAGES = {
    "maroc_telecom": "maroctelecom",
    "orange": "orangemaroc",
    "inwi": "inwi.ma",
}

# Version de l'API Graph à cibler explicitement (évite les changements de comportement
# silencieux si Meta bascule la version par défaut)
GRAPH_API_VERSION = "v19.0"

# Chemin de sortie des données brutes Facebook
FACEBOOK_RAW_OUTPUT_DIR = "data/raw/facebook"


# # -*- coding: utf-8 -*-
# """
# Configuration centrale du projet : identifiants des applications Google Play
# des trois opérateurs télécoms marocains ciblés.

# Emplacement : src/scraping/config.py
# """

# # Identifiants (package name) des applications officielles sur le Google Play Store.
# # Vérifiés manuellement sur play.google.com avant utilisation — à recontrôler
# # périodiquement, un opérateur peut changer d'app ou en publier une nouvelle.
# GOOGLE_PLAY_APPS = {
#     "maroc_telecom": {
#         "app_id": "com.MT.selfCare",
#         "app_name": "Mon Espace MT",
#     },
#     "orange": {
#         "app_id": "com.orange.meditel.mediteletmoi",
#         "app_name": "Orange et moi Maroc",
#     },
#     "inwi": {
#         "app_id": "ma.inwi.selfcaremobile",
#         "app_name": "My inwi",
#     },
# }

# # Paramètres de scraping
# LANG = "fr"          # langue demandée à l'API (n'empêche pas la darija/arabe dans les avis)
# COUNTRY = "ma"        # store marocain
# SORT_ORDER = "newest"  # on trie par récence pour prioriser les avis actuels

# # Chemin de sortie des données brutes (relatif à la racine du projet)
# RAW_OUTPUT_DIR = "data/raw/google_play"