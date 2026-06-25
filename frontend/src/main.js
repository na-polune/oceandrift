import "./style.css";

import { createViewer } from "./viewer.js";
import { fetchField, API_BASE } from "./api.js";
import { addCurrentLayer } from "./currentLayer.js";

const status = document.getElementById("status");

function setStatus(text, isError = false) {
  status.textContent = text;
  status.classList.toggle("error", isError);
}

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
    setStatus(
      `Surface currents — ${field.width}×${field.height} grid. Drag to spin the globe.`,
    );
    setTimeout(() => status.classList.add("fade"), 3000);
  } catch (error) {
    setStatus(
      "Currents loaded, but the globe failed to render — a WebGL/GPU browser is required.",
      true,
    );
    console.error(error);
  }
}

main();
