import React, { useEffect, useState } from "react";
import LayerSelector from "./components/LayerSelector";
import TimeIntervalSelector from "./components/TimeIntervalSelector";
import TimeSlider from "./components/TimeSlider";
import Heatmap from "./components/map";
import DiseaseSelector from "./components/selectDisease";


function App() {
  const [startDate, setStartDate] = useState(new Date().toISOString().slice(0, 10));
  const [interval, setInterval] = useState(365);
  const [offsetHuman, setOffsetHuman] = useState(0);
  const [offsetTemperature, setOffsetTemperature] = useState(0);
  const [desease, setDesease] = useState("Leishmania");
  const [geojsonList, setGeojsonList] = useState([]);
  const [selectedLayers, setSelectedLayers] = useState([]);
  const [selectedDate, setSelectedDate] = useState(startDate);
  const [selectedDisease, setSelectedDisease] = useState("Leishmania");
  //const [selectedLayer, setSelectedLayer] = useState("z_value");


  useEffect(() => {
  
    // Configuración de las solicitudes
    const filteredRequest = fetch("http://localhost:8000/api/test/filtered", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        start_date: "2022-01-01",
        interval: interval,
        desease: selectedDisease,
      }), 
    }).then((res) => res.json());
  
    const aemetRequest = fetch("http://localhost:8000/api/aemet/get_data", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        start_date: "2022-01-01",
        interval: interval,
      }),
    }).then((res) => res.json());
  
    // Ejecutar ambas solicitudes en paralelo
    Promise.all([filteredRequest, aemetRequest])
    .then(([filteredData, aemetData]) => {
      const processedFiltered = filteredData.map((item) => ({
        ...item,
        source: "filtered"
      }));
  
      const processedAemet = aemetData.map((item) => ({
        ...item,
        source: "aemet"
      }));
  
      setGeojsonList([...processedFiltered, ...processedAemet]);
      });
  }, [startDate, interval, desease]);

  return (
      <div style={{ width: "100vw", height: "100vh", position: "relative" }}>
          {/* renderiza el mapa */}
          <Heatmap
            deseaseData={geojsonList.find((item) => item.date === selectedDate && item.source === "filtered")?.geojson}
            aemetData={geojsonList.find((item) => item.date === selectedDate && item.source === "aemet")?.geojson}
            selectedLayers={selectedLayers}
          />

        {/* contenedor para el timeSlider, timeIntervalSelector y layerSelector */}
        <div
          style={{
            position: "absolute",
            top: "20px",
            right: "20px",
            zIndex: 10,
            backgroundColor: "white",
            padding: "20px",
            borderRadius: "12px",
            boxShadow: "0 4px 12px rgba(0,0,0,0.2)",
            width: "260px",
            display: "flex",
            flexDirection: "column",
            gap: "15px",
          }}
        >
          {/* renderiza el resto de componentes */}
        <TimeIntervalSelector interval={interval} setInterval={setInterval} />
        <TimeSlider
          dates={[...new Set(geojsonList.map((item) => item.date))].sort()}
          selectedDate={selectedDate}
          setSelectedDate={setSelectedDate}
        />
        <LayerSelector selectedLayers={selectedLayers} setSelectedLayers={setSelectedLayers} offsetHuman={offsetHuman} setOffsetHuman={offsetHuman} offsetTemperature={offsetHuman} setOffsetTemperature={setOffsetTemperature} />
        <DiseaseSelector selectedDisease={selectedDisease} setSelectedDisease={setSelectedDisease} />
      </div>
    </div>
  );
}

export default App;
