# Railway map data

© [OpenStreetMap contributors](https://www.openstreetmap.org/copyright).

The derived railway database in `assets/rail-data.js` is made available under the [Open Data Commons Open Database License (ODbL) 1.0](https://opendatacommons.org/licenses/odbl/1-0/). It includes native railway geometry, way IDs, selected tags and named station nodes, filtered to intersect a 1000 km radius of Beijing. Attribution and share-alike terms apply to the database.

The database is UTF-8 JSON compressed with gzip and encoded as base64 in `window.RAIL_DATA_PACKED`. It can be decoded with standard gzip/base64 tools. `assets/rail-data-metadata.json` describes the snapshot. `build_rail_map.py` documents extraction and transformation. Rail coordinates are WGS84. Map display uses Web Mercator; pixel-level cartographic rendering is not a survey.

Basemap: [OpenFreeMap](https://openfreemap.org/), based on OpenStreetMap and OpenMapTiles; retain the on-map attribution. The local basemap style is derived from OpenFreeMap Positron.

Map rendering library: [MapLibre GL JS 5.6.1](https://github.com/maplibre/maplibre-gl-js/tree/v5.6.1), BSD 3-Clause. Its license is included at `assets/maplibre-LICENSE.txt`.

Travel times are entered by the user. No example travel times or live train schedules are supplied with the map.
