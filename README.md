# oceandrift

Simulating Earth's ocean currents and how things drift on them.

> 🚧 Early work in progress.

## About

`oceandrift` models large-scale ocean surface currents and the drift of objects
carried by them. It runs entirely offline — no data downloads and no API keys
required.

## Getting started

```bash
pip install -r requirements.txt
pip install -e backend

python backend/scripts/plot_field.py   # render the current map
python backend/scripts/plot_drift.py   # drift particles and plot their tracks
pytest backend/tests                   # run the checks
```

## License

MIT
