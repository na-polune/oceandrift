import * as Cesium from "cesium";

/**
 * Create a Cesium Viewer that renders fully offline: the bundled Natural Earth
 * II imagery (shipped inside the cesium package), the default ellipsoid (no
 * terrain), and no Ion / network widgets.
 *
 * @param {string} containerId - id of the DOM element to mount the globe in.
 * @returns {Cesium.Viewer}
 */
export function createViewer(containerId) {
  // Belt and braces: never contact Cesium Ion.
  Cesium.Ion.defaultAccessToken = "";

  const viewer = new Cesium.Viewer(containerId, {
    baseLayer: Cesium.ImageryLayer.fromProviderAsync(
      Cesium.TileMapServiceImageryProvider.fromUrl(
        Cesium.buildModuleUrl("Assets/Textures/NaturalEarthII"),
      ),
    ),
    // terrainProvider omitted -> default EllipsoidTerrainProvider (offline).
    baseLayerPicker: false, // references online Ion/Bing sources
    geocoder: false, // calls api.cesium.com
    homeButton: false,
    sceneModePicker: false,
    navigationHelpButton: false,
    fullscreenButton: false,
    infoBox: false,
    selectionIndicator: false,
    timeline: true, // drift animation needs the clock UI (M5)
    animation: true,
    creditContainer: document.createElement("div"), // hide the credit overlay
  });

  viewer.scene.globe.enableLighting = false;
  viewer.scene.skyAtmosphere.show = true;
  viewer.scene.globe.depthTestAgainstTerrain = false;

  // Default view over the Atlantic, kept moderately close: from very far the
  // wind-layer particles fail the globe depth test and vanish.
  viewer.camera.setView({
    destination: Cesium.Cartesian3.fromDegrees(-40, 25, 15_000_000),
  });

  return viewer;
}
