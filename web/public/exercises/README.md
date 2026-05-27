# Images d'exercices

Les images bundlées des exercices (`<slug>.jpg`) sont téléchargées ici par le script :

```sh
cd api
python scripts/fetch_exercise_images.py
```

Elles sont servies en statique (`/exercises/<slug>.jpg`) et mises en cache par le service
worker PWA pour un fonctionnement hors-ligne. Ce dossier (hors ce README) n'est pas versionné.
