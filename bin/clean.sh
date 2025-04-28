#!/bin/bash
# Supprime tous les délimiteurs markdown ``` et variantes dans les fichiers YAML, JSON et HTML de output/recipe_expert_crew

find "$(dirname "$0")/../output/recipe_expert_crew" -type f \( -name '*.yaml' -o -name '*.json' -o -name '*.html' \) | while read -r file; do
  # Supprime toutes les lignes contenant uniquement des ``` ou ```yaml ou ```json ou ```html
  sed -i.bak '/^```[a-zA-Z]*$/d' "$file"
  # Supprime les ``` isolés même s'ils sont entourés d'espaces
  sed -i.bak '/^``` *$/d' "$file"
  rm -f "$file.bak"
done
