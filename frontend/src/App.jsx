import React, { useEffect, useState } from "react";
import LayerSelector from "./components/LayerSelector";
import TimeIntervalSelector from "./components/TimeIntervalSelector";
import TimeSlider from "./components/TimeSlider";
import Heatmap from "./components/map";


function App() {
  const [startDate, setStartDate] = useState(new Date().toISOString().slice(0, 10));
  const [interval, setInterval] = useState(365);
  const [desease, setDesease] = useState("Leishmania");
  const [geojsonList, setGeojsonList] = useState([]);
  const [selectedDate, setSelectedDate] = useState(startDate);
  const [selectedLayer, setSelectedLayer] = useState("z_value");
  const [loading, setLoading] = useState(false);
  const [dataSource, setDataSource] = useState("all"); // "all", "filtered", "aemet"
  const filteredGeojsonList = geojsonList.filter((item) => {
    if (dataSource === "all") return true;
    return item.source === dataSource;
  });

  useEffect(() => {
    setLoading(true);
  
    // Configuración de las solicitudes
    const filteredRequest = fetch("http://localhost:8000/api/test/filtered", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        start_date: startDate,
        end_date: "2025-12-31",
        interval: interval,
        desease: desease,
      }), 
    }).then((res) => res.json());
  
    const aemetRequest = fetch("http://localhost:8000/api/aemet/get_data", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        start_date: startDate,
        end_date: "2025-12-31",
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
      setLoading(false);
      });
  }, [startDate, interval, desease]);

  return (
      <div style={{ width: "100vw", height: "100vh", position: "relative" }}>
          {/* renderiza el mapa */}
          <Heatmap
            deseaseData={geojsonList.find((item) => item.date === selectedDate && item.source === "filtered")?.geojson}
            aemetData={geojsonList.find((item) => item.date === selectedDate && item.source === "aemet")?.geojson}
            selectedLayer={selectedLayer}
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
        <LayerSelector selectedLayer={selectedLayer} setSelectedLayer={setSelectedLayer} />
        <div>
          <label>Data Source:</label>
          <select value={dataSource} onChange={(e) => setDataSource(e.target.value)}>
            <option value="all">All</option>
            <option value="filtered">Filtered</option>
            <option value="aemet">AEMET</option>
          </select>
        </div>
      </div>
    </div>
  );
}

export default App;
