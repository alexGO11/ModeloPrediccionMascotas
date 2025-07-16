import maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import React, { useEffect, useRef } from "react";

const Heatmap = ({ diseaseData, aemetData, selectedLayers }) => {
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
        // Cargar datos de enfermedades
        map.current.addSource("disease-source", {
          type: "geojson",
          data: { type: "FeatureCollection", features: [] },
        });

        // Cargar datos de AEMET
        map.current.addSource("aemet-source", {
          type: "geojson",
          data: { type: "FeatureCollection", features: [] },
        });

        // Capa de mapa de temperatura
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
        

        map.current.addLayer({
          id: "disease-heatmap", 
          type: "heatmap",
          source: "disease-source",
          paint: {
            // El peso del heatmap debe basarse en el valor absoluto del z_value_normalized
            // para que tanto hot como cold spots tengan intensidad.
            // Ajustamos el rango de entrada para la interpolación del peso.
            "heatmap-weight": [
              "interpolate",
              ["linear"],
              ["get", "z_value_normalized"], // Usamos el valor normalizado entre 0 y 1
              0, 0.0, // El extremo más bajo (coldest)
              0.5, 0.05, // El centro (neutro)
              1, 1.0 // El extremo más alto (hottest)
            ],
            
            // La intensidad del heatmap. Ajusta según el zoom.
            "heatmap-intensity": ["interpolate", ["linear"], ["zoom"], 0, 1, 9, 3],
            
            // Colores del heatmap: Gradiente divergente (azul para frío, blanco/gris para neutro, rojo para caliente)
            "heatmap-color": [
              "interpolate",
              ["linear"],
              ["heatmap-density"], // La densidad calculada por MapLibre
              0, "rgba(0,0,255,0)", // Transparente o muy suave para zonas sin densidad
              
              // Cold spots (valores bajos de Z-score normalizado, cercanos a 0)
              0.1, "rgba(0, 0, 255, 0.4)",  // Azul claro
              0.2, "rgba(0, 0, 255, 0.6)",  // Azul medio
              0.3, "rgba(0, 0, 255, 0.8)",  // Azul oscuro

              // Valores neutros (Z-score normalizado cercano a 0.5)
              0.4, "rgba(255, 255, 255, 0.2)", // Blanco muy suave o gris claro
              0.5, "rgba(255, 255, 255, 0.4)", // Blanco o gris

              // Hot spots (valores altos de Z-score normalizado, cercanos a 1)
              0.6, "rgba(255, 165, 0, 0.6)", // Naranja
              0.7, "rgba(255, 69, 0, 0.8)",  // Rojo anaranjado
              0.8, "rgba(255, 0, 0, 1)"    // Rojo vivo
            ],
            
            // Radio del heatmap. Ajusta según el zoom.
            "heatmap-radius": ["interpolate", ["linear"], ["zoom"], 0, 2, 9, 20],
            
            // Opacidad del heatmap. A menudo se desvanece a ciertos niveles de zoom.
            "heatmap-opacity": ["interpolate", ["linear"], ["zoom"], 7, 1, 9, 0]
          },
        });

        map.current.addLayer({
          id: "aemet-hover-layer",
          type: "circle",
          source: "aemet-source",
          paint: {
            "circle-radius": 5,
            "circle-color": "transparent"
          }
        });

        map.current.addLayer({
          id: "disseases-hover-layer",
          type: "circle",
          source: "disease-source",
          paint: {
            "circle-radius": 5,
            "circle-color": "transparent"
          }
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

  // Actualizar datos de enfermedades
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
    if (!map.current) return;
    
    //comprueba que capas estan en el array de capas seleccionadas
    const showTemp = selectedLayers.includes("temperature");
    const showHuman = selectedLayers.includes("human");
  
    if (map.current.getLayer("aemet-heatmap")) {
      map.current.setLayoutProperty("aemet-heatmap", "visibility", showTemp ? "visible" : "none");
    }
  }, [selectedLayers]);

  return <div ref={mapContainer} style={{ width: "100%", height: "100vh" }} />;
};

export default Heatmap;