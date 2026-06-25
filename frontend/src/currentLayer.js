import { WindLayer } from "cesium-wind-layer";

// A bright white -> cyan -> green -> yellow -> red ramp by current speed.
// Starts near-white (not blue) so slow currents stay visible over the ocean.
const SPEED_COLORS = [
  "#ffffff",
  "#bfefff",
  "#5fd0ff",
  "#8cff6a",
  "#ffe34d",
  "#ff9a3d",
  "#ff3b2f",
];

/**
 * Convert a /field payload into the WindData shape cesium-wind-layer expects.
 *
 * The plugin reads the flattened arrays row-major as index = y * width + x with
 * x running west->east and (with flipY:false) row 0 = the southern edge. Our
 * /field grid is stored south->north, so it lines up with the default; if the
 * currents ever render vertically mirrored, flip `flipY` in addCurrentLayer.
 */
export function buildWindData(field) {
  const [west, south, east, north] = field.bbox;
  return {
    u: {
      array: Float32Array.from(field.u),
      min: field.u_range[0],
      max: field.u_range[1],
    },
    v: {
      array: Float32Array.from(field.v),
      min: field.v_range[0],
      max: field.v_range[1],
    },
    width: field.width,
    height: field.height,
    bounds: { west, south, east, north },
  };
}

/**
 * Add an animated current particle layer to the viewer.
 *
 * @param {import('cesium').Viewer} viewer
 * @param {object} field - a /field payload
 * @param {object} [options] - overrides for WindLayerOptions
 * @returns {WindLayer}
 */
export function addCurrentLayer(viewer, field, options = {}) {
  const windData = buildWindData(field);
  return new WindLayer(viewer, windData, {
    particlesTextureSize: 180, // ~32k particles for fuller coverage
    // Lift particles well above the surface so they pass the globe depth test
    // (at far camera distances a low height makes every particle get discarded).
    particleHeight: 100000,
    // Seed particles only in the current view so the visible ocean stays dense
    // instead of being spread thin across the whole globe.
    useViewerBounds: true,
    lineWidth: { min: 2, max: 4.5 },
    lineLength: { min: 40, max: 160 },
    // The layer scales motion by (pixelSize+50)*speedFactor, which is already
    // huge at this zoom, so keep speedFactor modest and clamp speed->colour to m/s.
    speedFactor: 1.0,
    domain: { min: 0, max: 2 },
    displayRange: { min: 0, max: 2 },
    dropRate: 0.008, // reseed often so the field stays populated (no fade-out)
    dropRateBump: 0.01,
    colors: SPEED_COLORS,
    flipY: false, // our /field grid is already south->north
    dynamic: true,
    ...options,
  });
}
