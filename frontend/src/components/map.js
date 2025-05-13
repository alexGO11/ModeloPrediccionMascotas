import maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import React, { useEffect, useRef } from "react";

const Heatmap = ({ deseaseData, aemetData, selectedLayer }) => {
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
        // Enfermedades
        map.current.addSource("heatmap-source", {
          type: "geojson",
          data: { type: "FeatureCollection", features: [] },
        });

        map.current.addSource("aemet-source", {
          type: "geojson",
          data: { type: "FeatureCollection", features: [] },
        });


        map.current.addLayer({
          id: 'aemet-heatmap',
          type: 'heatmap',
          source: 'aemet-source',
          paint: {
            // Peso de cada punto según su temperatura
            'heatmap-weight': [
              'interpolate',
              ['linear'],
              ['get', 'temp'],
              0, 0,
              40, 1
            ],
        
            // Ajusta la intensidad según el zoom (más intensidad al acercar)
            'heatmap-intensity': [
              'interpolate',
              ['linear'],
              ['zoom'],
              0, 0.5,
              9, 1.5
            ],
        
            // Cambia el radio según el zoom
            'heatmap-radius': [
              'interpolate',
              ['linear'],
              ['zoom'],
              0, 2,
              5, 10,
              9, 25
            ],
        
            // Opcional: reduce opacidad al alejar para no saturar
            'heatmap-opacity': [
              'interpolate',
              ['linear'],
              ['zoom'],
              0, 0.3,
              7, 0.5,
              10, 0.4
            ],
        
           'heatmap-color': [
              'interpolate',
              ['linear'],
              ['heatmap-density'],
              0, 'rgba(0, 0, 255, 0)',
              0.1, 'blue',
              0.2, 'cyan',
              0.4, 'lime',
              0.6, 'yellow',
              0.8, 'orange',
              1, 'red'
            ],
          }
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

        map.current.addLayer({
            id: 'etiquetas-temperatura',
            type: 'symbol',
            source: 'temperaturas',
            layout: {
              'text-field': ['concat', ['to-string', ['get', 'temp']], '°C'],
              'text-size': 10,
              'text-offset': [0, 0.5],
              'text-anchor': 'top'
            },
            paint: {
              'text-color': '#ffffff'
            }
        });
        

        map.current.addLayer({
          id: "disseases-hover-layer",
          type: "fill",
          source: "heatmap-source",
          layout: {},
          paint: {
            "fill-color": "rgb(103,169,207)",
            "fill-opacity": 0,
          },
        });

        // Mostrar popup al pasar el ratón (solo enfermedades)
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

        map.current.on("mouseleave", "hover-layer", () => {
          popupRef.current.remove();
        });
      });
    }
  }, []);

  // Actualizar datos de enfermedades
  useEffect(() => {
    if (map.current && map.current.getSource("heatmap-source") && deseaseData) {
      map.current.getSource("heatmap-source").setData(deseaseData);
    }
  }, [deseaseData]);
  
  useEffect(() => {
    if (map.current && map.current.getSource("aemet-source") && aemetData) {
      map.current.getSource("aemet-source").setData(aemetData);
    }
  }, [aemetData]);
  


  useEffect(() => {
    if (!map.current) return;
  
    const showDesease = selectedLayer === "z_value" || selectedLayer === "all";
    const showTemp = selectedLayer === "temperatura" || selectedLayer === "all";
  
    if (map.current.getLayer("heatmap-layer")) {
      map.current.setLayoutProperty("heatmap-layer", "visibility", showDesease ? "visible" : "none");
    }
    if (map.current.getLayer("aemet-heatmap")) {
      map.current.setLayoutProperty("aemet-heatmap", "visibility", showTemp ? "visible" : "none");
    }
  }, [selectedLayer]);

  return <div ref={mapContainer} style={{ width: "100%", height: "100vh" }} />;
};

export default Heatmap;
