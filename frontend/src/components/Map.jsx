import maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import React, { useEffect, useRef } from "react";

const Heatmap = ({ diseaseData, aemetData, humanData, selectedLayers }) => {
  const mapContainer = useRef(null);
  const map = useRef(null);
  const popupRef = useRef(new maplibregl.Popup({ closeButton: false, closeOnClick: false }));

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
        // Load initial empty sources

        // Disease data
        map.current.addSource("disease-source", {
          type: "geojson",
          data: { type: "FeatureCollection", features: [] },
        });

        // AEMET data
        map.current.addSource("aemet-source", {
          type: "geojson",
          data: { type: "FeatureCollection", features: [] },
        });

        // Human data
        map.current.addSource("human-source", {
          type: "geojson",
          data: { type: "FeatureCollection", features: [] },
        });

        // Layer for human data
        map.current.addLayer({
          id: "human-layer",
          type: "circle",
          source: "human-source",
          paint: {
            'circle-radius': 8,
            "circle-color": [
              "interpolate",
              ["linear"],
              ["get", "cases"],   
              1, "rgba(255, 255, 0, 0.6)",   
              2, "rgba(255, 165, 0, 0.7)",   
              3, "rgba(255, 0, 0, 0.8)"      
            ],
          }
        });

        // Layer for AEMET data
        map.current.addLayer({
          id: 'aemet-heatmap',
          type: 'circle',
          source: 'aemet-source',
            paint: {
              'circle-radius': 4,
              'circle-color': [
                'interpolate', ['linear'], ['get', 'temp_norm'],
                0, 'rgba(0, 0, 255, 0)',
                0.1, 'blue',
                0.2, 'cyan',
                0.4, 'lime',
                0.6, 'yellow',
                0.8, 'orange',
                1, 'red'
              ],
              'circle-opacity': 0.4
            }
        });
        
        // Layer for disease data
        map.current.addLayer({
          id: "disease-heatmap", 
          type: "heatmap",
          source: "disease-source",
          paint: {
            "heatmap-weight": [
              "interpolate",
              ["linear"],
              ["get", "z_value_normalized"], 
              0, 0.0, 
              0.5, 0.05,
              1, 1.0
            ],
            
            "heatmap-intensity": ["interpolate", ["linear"], ["zoom"], 0, 1, 9, 3],
            
            "heatmap-color": [
              "interpolate",
              ["linear"],
              ["heatmap-density"], 
              0, "rgba(0,0,255,0)", 
              
             
              0.1, "rgba(0, 0, 255, 0.4)",  
              0.2, "rgba(0, 0, 255, 0.6)",  
              0.3, "rgba(0, 0, 255, 0.8)",  

              
              0.4, "rgba(255, 255, 255, 0.2)", 
              0.5, "rgba(255, 255, 255, 0.4)", 

              
              0.6, "rgba(255, 165, 0, 0.6)", 
              0.7, "rgba(255, 69, 0, 0.8)",  
              0.8, "rgba(255, 0, 0, 1)"   
            ],
            
            "heatmap-radius": ["interpolate", ["linear"], ["zoom"], 0, 2, 9, 20],
            
            "heatmap-opacity": ["interpolate", ["linear"], ["zoom"], 7, 1, 9, 0]
          },
        });

        // Hover layers for popups

        // AEMET hover layer
        map.current.addLayer({
          id: "aemet-hover-layer",
          type: "circle",
          source: "aemet-source",
          paint: {
            "circle-radius": 5,
            "circle-color": "transparent"
          }
        });

        // Disease hover layer
        map.current.addLayer({
          id: "disseases-hover-layer",
          type: "circle",
          source: "disease-source",
          paint: {
            "circle-radius": 5,
            "circle-color": "transparent"
          }
        });

        const popup = new maplibregl.Popup({
          closeButton: false,
          closeOnClick: false
        });

        // Event listeners on hover layers for popups
        map.current.on("mousemove", "human-layer", (e) => {
          const feature = e.features[0];
          const { post_code, cases } = feature.properties;

          popup
            .setLngLat(e.lngLat)
            .setHTML(
              `<strong>Código postal:</strong> ${post_code}<br/><strong>Casos:</strong> ${cases}`
            )
            .addTo(map.current);
        });

        map.current.on("mouseleave", "human-layer", () => {
          popup.remove();
        });
        
        map.current.on("mousemove", "aemet-hover-layer", (e) => {
          const feature = e.features[0];
          const { temp, temp_norm } = feature.properties;

          popupRef.current
            .setLngLat(e.lngLat)
            .setHTML(
              `<strong>Temperatura media:</strong> ${temp}<br/><strong>Temperatura normalizada:</strong> ${temp_norm}`
            )
            .addTo(map.current);
        });

        map.current.on("mouseleave", "aemet-hover-layer", () => {
          popupRef.current.remove();
        });

        map.current.on("mousemove", "disseases-hover-layer", (e) => {
          const feature = e.features[0];
          const { post_code, z_value, n_positives } = feature.properties;

          popupRef.current
            .setLngLat(e.lngLat)
            .setHTML(
              `<strong>Código postal:</strong> ${post_code}<br/><strong>Z:</strong> ${z_value}<br/><strong>Num. Positives:</strong> ${n_positives}`
            )
            .addTo(map.current);
        });

        map.current.on("mouseleave", "disseases-hover-layer", () => {
          popupRef.current.remove();
        });
      });
    }
  }, []);

  // Update sources when data changes
  useEffect(() => {
    if (map.current && map.current.getSource("disease-source") && diseaseData) {
      map.current.getSource("disease-source").setData(diseaseData);
    }
  }, [diseaseData]);
  
  useEffect(() => {
    if (map.current && map.current.getSource("aemet-source") && aemetData) {
      map.current.getSource("aemet-source").setData(aemetData);
    }
  }, [aemetData]);


  useEffect(() => {
    if (map.current && map.current.getSource("human-source") && humanData) {
      map.current.getSource("human-source").setData(humanData);
    }
  }, [humanData]);
  


  useEffect(() => {
    if (!map.current) return;

    // Show or hide layers based on selectedLayers
    
    const showTemp = selectedLayers.includes("temperature");
    const showHuman = selectedLayers.includes("human");
  
    if (map.current.getLayer("aemet-heatmap")) {
      map.current.setLayoutProperty("aemet-heatmap", "visibility", showTemp ? "visible" : "none");
    }
    if (map.current.getLayer("human-layer")) {
      map.current.setLayoutProperty("human-layer", "visibility", showHuman ? "visible" : "none");
    }
  }, [selectedLayers]);

  return <div ref={mapContainer} style={{ width: "100%", height: "100vh" }} />;
};

export default Heatmap;