# Sela Project- Posts WebApp

General summary of my project
## Application

The project contains a python web app that let's you sign up/in, create posts, and see and like other people posts

### DataBase: MongoDB
The database contains a database with two collections: Users (username + password) and posts (title, content, username of poster, list of usernames that liked the post)

### Jenkins Pipeline
Whenever a push is made to the feature branch of this repo, a pipeline is triggered and builds the app's image with a "temp" tag, runs docker-compose that builds mongodb, app, and pytest, runs the unit tests in the test_main, and sends a merge request to the repo.
If we approve the merge, the pipeline runs again in the detected 'main' branch, and retests, pushed a new image for the app with a generated tag, and adds the tag to the helm charts before pakaging and pushing it (for argoCD detection)

### ArgoCD
ArgoCD detects a push to the helm registry, and should apply the new image to the app. For now, the sync happens automatically without changing the image, so we do hard-refresh and port-forward the new created pod.
