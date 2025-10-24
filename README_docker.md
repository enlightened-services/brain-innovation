# Run this site with Docker

## Prerequisites
- Docker and (optionally) Docker Compose installed

## Build and run (Compose)
```bash
docker compose up --build -d
```
Open: http://localhost:8082

## Build and run (Docker only)
```bash
docker build -t brainport-eindhoven-site:latest .
docker run --rm -p 8082:8000 brainport-eindhoven-site:latest
```

## Notes
- Content is served by Nginx from `/usr/share/nginx/html`.
- Use `infographic.html` to view the SVG reliably (avoids file:// issues).
- Stop Compose: `docker compose down`.

## Publish to GitHub Container Registry (GHCR)

Automated via GitHub Actions on pushes to `main` and tags `v*`.

Image will be published as:

- `ghcr.io/<owner>/<repo>:latest` (on `main`)
- `ghcr.io/<owner>/<repo>:<git-sha>`
- `ghcr.io/<owner>/<repo>:<tag>` (on tags `v*`)

Ensure Actions are enabled and packages permissions allow write. First time, set the package visibility to public in GitHub UI if you want a public image.

### Manual publish (local)
```bash
OWNER_REPO="$(git config --get remote.origin.url | sed -E 's#.*/([^/]+/[^/.]+)(\.git)?$#\1#' | tr '[:upper:]' '[:lower:]')"
IMAGE="ghcr.io/$OWNER_REPO:manual"
echo "$IMAGE"
echo "$GITHUB_TOKEN" | docker login ghcr.io -u "${GITHUB_ACTOR:-USERNAME}" --password-stdin
docker build -t "$IMAGE" .
docker push "$IMAGE"
```
