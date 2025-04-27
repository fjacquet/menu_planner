# Menu Planner with CrewAI

Menu Planner est un système de génération de menus hebdomadaires pour familles, propulsé par le framework CrewAI. Il orchestre plusieurs agents spécialisés pour :

- Rechercher et sélectionner des recettes adaptées (2 adultes, enfants)
- Analyser la valeur nutritionnelle et estimer les calories
- Adapter les recettes pour Thermomix
- Concevoir un menu hebdomadaire en HTML propre et responsive
- Générer une liste de courses avec quantités et cases à cocher
- Produire un poème ou des faits ludiques sur la nutrition
- Envoyer le menu final par e-mail via Gmail

## Fonctionnalités

- Architecture multi-agents grâce à [CrewAI](https://crewai.com)
- Configuration simple via fichier `.env`
- Sorties structurées : JSON, HTML, liste de recettes, shopping list, poème
- Intégration d’APIs externes : Composio, SerpAPI, OpenAI/Gemini
- Respect des principes KISS & DRY

## Prérequis

- Python 3.10 ≤ version < 3.13
- [UV](https://docs.astral.sh/uv/) pour la gestion des dépendances
- Clés API (Composio, SerpAPI, Gemini/OpenAI, Gmail)

## Installation

```bash
pip install uv
uv install
```

### Configuration

```bash
cp .env.sample .env
# Éditez .env avec vos clés et préférences
```

## Lancer le flux

```bash
crewai flow kickoff
```

Les fichiers générés se trouvent dans `output/menu_designer_crew` :

- `menu.json` : données du menu structuré
- `menu.html` : page HTML stylée
- `liste_recettes.json` : titres des recettes
- `shopping_list.json` : liste de courses
- Poème/faits nutritionnels

## Variables d’environnement

| Clé                      | Description                                   |
|--------------------------|-----------------------------------------------|
| `ADULTS`                 | Nombre d’adultes                              |
| `CHILDREN`               | Nombre d’enfants                              |
| `CHILDREN_AGE`           | Âge des enfants                               |
| `MAILTO`                 | Destinataire du menu (e-mail)                 |
| `COMPOSIO_API_KEY`       | Clé d’API Composio                            |
| `COMPOSIO_SERPAPI_API_KEY`| Clé SerpAPI pour Composio                     |
| `GEMINI_API_KEY`         | Clé API Gemini                                |
| `OPENAI_API_KEY`         | Clé API OpenAI                                |
| `MODEL`                  | Modèle LLM (ex : `gemini/gemini-2.0-flash`)    |
| `OPENAI_TIMEOUT`         | Timeout OpenAI (secondes)                     |
| `LITELLM_TIMEOUT`        | Timeout LitelLM (secondes)                    |

## Structure du projet

```
menu_planner/
├── src/menu_planner/
│   ├── main.py         # Point d’entrée du flow
│   ├── schemas.py      # Modèles Pydantic et état global
│   └── crews/
│       ├── poem_crew/
│       ├── recipe_expert_crew/
│       ├── menu_designer_crew/
│       ├── shopping_crew/
│       └── html_design_crew/
├── config/
│   ├── agents.yaml     # Configuration des agents
│   └── tasks.yaml      # Configuration des tâches
├── .env.sample         # Modèle de variables d’environnement
└── output/             # Résultats générés
```

## Contribuer

Les contributions sont les bienvenues : ouvrez une issue ou proposez une PR.

## Licence

MIT 
