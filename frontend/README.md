# oceandrift — frontend

A CesiumJS 3D globe that renders the toy ocean's surface currents as animated
GPU particles, fed by the backend API. Runs fully offline (bundled Natural Earth
imagery, no Cesium Ion account or token).

## Run

The globe needs the backend API running first:

```bash
# 1) start the API (from the repo root)
python -m oceanapi                 # http://127.0.0.1:8000

# 2) start the globe (from frontend/)
npm install                        # first time only
npm run dev                        # http://localhost:5173
```

Then open **http://localhost:5173** in a WebGL-capable browser (Chrome, Edge,
Firefox). Drag to spin the globe; the coloured streaks are the surface currents.

## How it works

| File | Role |
| --- | --- |
| `src/viewer.js` | Offline Cesium Viewer — bundled Natural Earth II imagery, no Ion |
| `src/api.js` | Fetches `GET /field` from the backend |
| `src/currentLayer.js` | Builds a `cesium-wind-layer` `WindLayer` (GPU particles) from the field |
| `src/main.js` | Wires it together |

Point the app at a different backend with a `.env` (see `.env.example`):

```
VITE_API_BASE=http://127.0.0.1:8000
```

## Notes

- Rendering requires a GPU/WebGL2 browser — a headless/software context won't work.
- If the currents ever appear vertically mirrored, toggle `flipY` in
  `src/currentLayer.js`.
