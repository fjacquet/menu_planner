# Menu Planner with CrewAI

![CrewAI Badge](https://img.shields.io/badge/Built%20with-CrewAI-blue) ![Python Version](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-green) ![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

## Vue d'ensemble

Menu Planner est un système avancé de planification de menus mensuels pour familles, propulsé par le framework CrewAI. Cette application orchestrée par IA divise intelligemment les tâches entre plusieurs agents spécialisés pour créer une expérience complète de planification alimentaire.

### Agents spécialisés

- **Menu Designer**: Recherche et sélectionne des recettes adaptées aux besoins familiaux
- **Recipe Expert**: Analyse nutritionnelle et adaptation des recettes (compatible Thermomix)
- **Shopping Crew**: Génération d'une liste de courses organisée par catégorie
- **HTML Design Crew**: Création d'une présentation visuelle du menu mensuel
- **Poem Crew**: Génération de contenu créatif sur le thème de la nutrition

### Caractéristiques principales

- **Architecture multi-agents** avec [CrewAI Flow](https://docs.crewai.com/concepts/Flow/) pour un traitement en parallèle
- **Génération complète de menu mensuel** couvrant déjeuners et dîners
- **Analyse nutritionnelle** avec estimation des calories
- **Adaptation Thermomix** des recettes pour une préparation simplifiée
- **Traitement parallèle des recettes** grâce à `kickoff_for_each` pour une exécution optimisée
- **Interface HTML responsive** pour consultation sur tous appareils
- **Liste de courses organisée** avec quantités et cases à cocher
- **Touche créative** avec poèmes ou faits ludiques sur la nutrition

## Architecture technique

- **Framework**: [CrewAI](https://crewai.com) pour l'orchestration multi-agents
- **Modèles**: Support de modèles locaux (Ollama) et cloud (OpenAI, Gemini)
- **Outils d'enrichissement**: SerplyWeb, ScrapeNinja pour la recherche et extraction web
- **Gestion dépendances**: [UV](https://docs.astral.sh/uv/) pour performance et reproductibilité
- **Configuration**: Variables d'environnement via fichier `.env`
- **Stockage**: Sortie structurée JSON/HTML/YAML dans répertoire `output/`

## Guide de démarrage

### Prérequis

- Python 3.10 ≤ version < 3.13
- [UV](https://docs.astral.sh/uv/) pour la gestion des dépendances
- Clés API pour les services intégrés (optionnellement, modèles locaux via Ollama)

### Installation

```bash
# Clone le dépôt
git clone https://github.com/yourusername/menu_planner.git
cd menu_planner

# Installation des dépendances
pip install uv
uv install
```

### Configuration

```bash
# Copier le modèle de configuration
cp .env.sample .env

# Éditer .env avec vos clés API et préférences
vim .env  # ou votre éditeur préféré
```

### Lancer l'application

```bash
# Générer un menu complet
uv run kickoff

# Ou pour générer une recette spécifique, modifier MaRecette dans main.py
# puis exécuter
uv run kickoff
```

## Structure des fichiers générés

Les fichiers de sortie sont organisés par crew dans le répertoire `output/` :

### Menu Designer Crew
- `menu.json` : Données complètes du menu mensuel structuré
- `menu.html` : Présentation HTML interactive et stylée du menu
- `liste_recettes.json` : Liste extraite de toutes les recettes du menu

### Recipe Expert Crew
- `recipe_name.html` : Page HTML détaillée pour chaque recette
- `recipe_name.yaml` : Données structurées de la recette au format YAML
- `recipe_name_ingredients.json` : Liste des ingrédients pour la liste de courses

### Shopping Crew
- `liste_courses.html` : Liste de courses organisée par catégorie au format HTML
- `liste_courses.md` : Version Markdown de la liste de courses

## Variables d'environnement

| Variable               | Description                                          | Exemple                    |
|------------------------|------------------------------------------------------|----------------------------|  
| `ADULTS`               | Nombre d'adultes dans le foyer                       | `2`                        |
| `CHILDREN`             | Nombre d'enfants                                     | `1`                        |
| `CHILDREN_AGE`         | Âge des enfants (influençant les recettes)           | `10`                       |
| `MAILTO`               | Adresse email pour envoi du menu                     | `user@example.com`         |
| `MODEL_NAME`           | Modèle LLM à utiliser (local ou API)                 | `ollama/gemma3:latest`     |
| `API_BASE`             | URL de base pour les modèles locaux Ollama           | `http://localhost:11434`   |
| `OPENAI_API_KEY`       | Clé API OpenAI (si utilisation de modèles OpenAI)    | `sk-...`                   |
| `GEMINI_API_KEY`       | Clé API Gemini (si utilisation de modèles Google)    | `...`                      |
| `SERPLY_API_KEY`       | Clé API pour les recherches web via Serply           | `...`                      |
| `LITELLM_TIMEOUT`      | Délai d'attente pour les appels de modèles (sec)     | `300`                      |

## Architecture détaillée

```
menu_planner/
├── src/menu_planner/
│   ├── main.py         # Orchestration du flow avec CrewAI Flow
│   ├── schemas.py      # Modèles Pydantic pour validation et état global
│   ├── tools/          # Outils personnalisés (scrapeninja, etc.)
│   └── crews/          # Organisation des agents par spécialité
│       ├── poem_crew/              # Génération de poèmes
│       │   ├── config/            # Configuration YAML des agents et tâches
│       │   └── poem_crew.py       # Implémentation des agents
│       ├── recipe_expert_crew/    # Analyse et adaptation des recettes
│       ├── menu_designer_crew/    # Création du menu mensuel
│       ├── shopping_crew/         # Génération de liste de courses
│       └── html_design_crew/      # Présentation visuelle
├── .env.sample         # Modèle de configuration
└── output/             # Résultats générés organisés par crew
```

## Traitement parallèle

Le système utilise `crew.kickoff_for_each()` pour traiter plusieurs recettes en parallèle, accélérant considérablement le temps d'exécution par rapport au traitement séquentiel. Cette optimisation est particulièrement efficace lors de la génération d'un menu mensuel complet.

## Contribution

Les contributions sont les bienvenues ! Pour contribuer :

1. Forkez le projet
2. Créez une branche pour votre fonctionnalité (`git checkout -b feature/amazing-feature`)
3. Committez vos changements (`git commit -m 'Add some amazing feature'`)
4. Poussez vers la branche (`git push origin feature/amazing-feature`)
5. Ouvrez une Pull Request

## Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## Contact

Pour toute question ou suggestion, n'hésitez pas à ouvrir une issue dans ce dépôt.
