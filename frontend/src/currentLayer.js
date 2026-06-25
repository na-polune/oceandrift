import { WindLayer } from "cesium-wind-layer";

// A blue -> green -> yellow -> red ramp by current speed.
const SPEED_COLORS = [
  "#2c7bb6",
  "#00a6ca",
  "#00ccbc",
  "#90eb9d",
  "#ffff8c",
  "#f9d057",
  "#f29e2e",
  "#e76818",
  "#d7191c",
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
    particlesTextureSize: 128, // ~16k particles
    lineWidth: { min: 1, max: 3 },
    lineLength: { min: 40, max: 160 },
    // Ocean currents are slow (~0.1-1 m/s); boost so the motion reads on screen.
    speedFactor: 12.0,
    dropRate: 0.003,
    dropRateBump: 0.01,
    colors: SPEED_COLORS,
    flipY: false, // our /field grid is already south->north
    dynamic: true,
    ...options,
  });
}
