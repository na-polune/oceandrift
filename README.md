# oceandrift

Simulating Earth's ocean currents and how things drift on them.

> 🚧 Early work in progress.

## About

`oceandrift` models large-scale ocean surface currents and the drift of objects
carried by them — buoys, spills, debris. It runs entirely offline: no data
downloads and no API keys required.

The backend is two small, reusable Python libraries plus an HTTP API:

- **`oceanfield`** — an analytic toy model of global surface currents (gyres,
  equatorial currents, the Antarctic Circumpolar Current and eddies), masked to
  the ocean.
- **`oceandrift`** — a Lagrangian drift engine that traces where seeded
  particles travel on any current field.
- **`oceanapi`** — a FastAPI service exposing both.

## Install

```bash
pip install -r requirements.txt
pip install -e backend
```

## Run

```bash
# Visual sanity checks — writes PNGs to backend/scripts/figures/
python backend/scripts/plot_field.py   # the current map
python backend/scripts/plot_drift.py   # drift tracks

# HTTP API — interactive docs at /docs
python -m oceanapi                     # http://127.0.0.1:8000

# Tests
pytest backend/tests
```

### API

| Endpoint | Description |
| --- | --- |
| `GET /field` | Surface-current `u`/`v` sampled on a lon/lat grid |
| `POST /drift` | Seed particles, return their tracks as GeoJSON or CZML |

## Library use

```python
from oceanfield import ToyOceanField
from oceandrift import DriftEngine, DriftConfig, DAY

ocean = ToyOceanField()
u, v = ocean.velocity(lat=40.0, lon=-50.0)        # m/s, eastward & northward

engine = DriftEngine(ocean)
tracks = engine.run([35.0], [-60.0], DriftConfig(duration=60 * DAY))
```

## License

MIT
