import { defineConfig } from "vite";
import cesium from "vite-plugin-cesium";

// vite-plugin-cesium copies Cesium's static Assets/Workers/Widgets, sets
// CESIUM_BASE_URL, and injects widgets.css -- everything needed to run offline.
export default defineConfig({
  plugins: [cesium()],
  server: { port: 5173 },
  // cesium-wind-layer must share a single Cesium instance with the app;
  // dedupe prevents Vite from bundling two copies (a known cause of a broken
  // context / maxTextureSize 0).
  resolve: { dedupe: ["cesium"] },
});
