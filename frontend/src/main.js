import "./style.css";

import { createViewer } from "./viewer.js";
import { fetchField, fetchDrift, API_BASE } from "./api.js";
import { addCurrentLayer } from "./currentLayer.js";
import { addDriftTracks } from "./driftLayer.js";

const status = document.getElementById("status");

function setStatus(text, isError = false) {
  status.textContent = text;
  status.classList.toggle("error", isError);
}

// Default drifters for M5 (M6 will let you drop your own by clicking the globe).
const DRIFT_SEEDS = [
  { lat: 34, lon: -64 }, // N. Atlantic crossing
  { lat: 20, lon: -45 }, // N. Atlantic interior
  { lat: -28, lon: -42 }, // Brazil Current
  { lat: -33, lon: 58 }, // Agulhas / S. Indian
  { lat: -42, lon: -150 }, // S. Pacific gyre
  { lat: -20, lon: 90 }, // S. Indian east
];

async function main() {
  const viewer = createViewer("cesiumContainer");

  let field;
  try {
    setStatus("Loading surface currents…");
    field = await fetchField({ resolution: 1.5 });
  } catch (error) {
    setStatus(
      `Could not reach the API at ${API_BASE}. Is it running? (python -m oceanapi)`,
      true,
    );
    console.error(error);
    return;
  }

  try {
    addCurrentLayer(viewer, field);
  } catch (error) {
    setStatus(
      "Currents loaded, but the globe failed to render — a WebGL/GPU browser is required.",
      true,
    );
    console.error(error);
    return;
  }

  // M5: seed a few drifters and animate them along the currents on the clock.
  try {
    setStatus("Currents up. Running drift…");
    const czml = await fetchDrift({
      seeds: DRIFT_SEEDS,
      duration_days: 120,
      format: "czml",
    });
    await addDriftTracks(viewer, czml);
    setStatus(
      `${field.width}×${field.height} currents + ${DRIFT_SEEDS.length} drifters — press ▶ to play, drag to spin.`,
    );
    setTimeout(() => status.classList.add("fade"), 4000);
  } catch (error) {
    setStatus("Currents are up, but drift tracks failed to load.", true);
    console.error(error);
  }
}

main();
