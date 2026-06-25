import * as Cesium from "cesium";

/**
 * Load CZML drift tracks onto the globe and drive the viewer's clock from them,
 * so the drifters animate along the currents over time. Each drifter is styled
 * with a bright glowing trail of its full path so the trajectory is legible.
 *
 * @param {import('cesium').Viewer} viewer
 * @param {Array} czml - a CZML document (from POST /drift with format=czml)
 * @returns {Promise<import('cesium').CzmlDataSource>}
 */
export async function addDriftTracks(viewer, czml) {
  const dataSource = await Cesium.CzmlDataSource.load(czml);
  await viewer.dataSources.add(dataSource);

  // Make each drifter and its full trail clearly readable.
  for (const entity of dataSource.entities.values) {
    if (entity.point) {
      entity.point.pixelSize = 11;
      entity.point.color = Cesium.Color.ORANGE;
      entity.point.outlineColor = Cesium.Color.BLACK.withAlpha(0.7);
      entity.point.outlineWidth = 1.5;
    }
    if (entity.path) {
      entity.path.leadTime = 0;
      entity.path.trailTime = 1e9; // show the whole track behind the drifter
      entity.path.width = 3;
      entity.path.material = new Cesium.PolylineGlowMaterialProperty({
        glowPower: 0.25,
        color: Cesium.Color.ORANGE,
      });
    }
  }

  // Sync the viewer clock to the drift run and start playing.
  const clock = dataSource.clock;
  if (clock) {
    viewer.clock.startTime = clock.startTime.clone();
    viewer.clock.stopTime = clock.stopTime.clone();
    viewer.clock.currentTime = clock.currentTime.clone();
    viewer.clock.multiplier = clock.multiplier;
    viewer.clock.clockRange = clock.clockRange;
    if (viewer.timeline) {
      viewer.timeline.zoomTo(clock.startTime, clock.stopTime);
    }
  }
  viewer.clock.shouldAnimate = true;

  return dataSource;
}
