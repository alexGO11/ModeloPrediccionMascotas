import maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import React, { useEffect, useRef } from "react";

const Heatmap = ({ geojsonData }) => {
  const mapContainer = useRef(null);
  const map = useRef(null);

  useEffect(() => {
    if (!map.current) {
      map.current = new maplibregl.Map({
        container: mapContainer.current,
        style:
          "https://api.maptiler.com/maps/basic/style.json?key=UfS7gj1LT7QWhvbNSJi2",
        center: [-3.70379, 40.41678],
        zoom: 6,
      });

      map.current.on("load", () => {
        map.current.addSource("heatmap-source", {
          type: "geojson",
          data: { type: "FeatureCollection", features: [] },
        });

        map.current.addLayer({
          id: "heatmap-layer",
          type: "heatmap",
          source: "heatmap-source",
          paint: {
            "heatmap-weight": ["interpolate", ["linear"], ["get", "z_value"], 0, 0, 10, 1],
            "heatmap-intensity": ["interpolate", ["linear"], ["zoom"], 0, 1, 9, 3],
            "heatmap-color": [
              "interpolate",
              ["linear"],
              ["heatmap-density"],
              0,
              "rgba(33,102,172,0)",
              0.2,
              "rgb(103,169,207)",
              0.4,
              "rgb(209,229,240)",
              0.6,
              "rgb(253,219,199)",
              0.8,
              "rgb(239,138,98)",
              1,
              "rgb(178,24,43)",
            ],
            "heatmap-radius": ["interpolate", ["linear"], ["zoom"], 0, 2, 9, 20],
            "heatmap-opacity": ["interpolate", ["linear"], ["zoom"], 7, 1, 9, 0],
          },
        });
      });
    }
  }, []);

  useEffect(() => {
    if (geojsonData && map.current.getSource("heatmap-source")) {
      map.current.getSource("heatmap-source").setData(geojsonData);
    }
  }, [geojsonData]);

  return <div ref={mapContainer} style={{ width: "100%", height: "100vh" }} />;
};

export default Heatmap;
