import { defineConfig } from "vite";
import cesium from "vite-plugin-cesium";

// vite-plugin-cesium copies Cesium's static Assets/Workers/Widgets, sets
// CESIUM_BASE_URL, and injects widgets.css -- everything needed to run offline.
export default defineConfig({
  plugins: [cesium()],
  server: { port: 5173 },
});
