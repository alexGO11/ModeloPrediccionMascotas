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

  useEffect(() => {
    setLoading(true);
    fetch("http://localhost:8000/api/test/filtered", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        start_date: startDate,
        end_date: "2025-12-31",
        interval: interval,
        desease: desease,
      }),
    })
      .then((res) => res.json())
      .then((data) => {
        setGeojsonList(data);
        setSelectedDate(data[0]?.date);
        setLoading(false);
      })
      .catch((error) => {
        console.error("Error:", error);
        setLoading(false);
      });
  }, [startDate, interval, desease]);

  return (
      <div style={{ width: "100vw", height: "100vh", position: "relative" }}>
          {/* renderiza el mapa */}
        <Heatmap
          geojsonData={geojsonList.find((item) => item.date === selectedDate)?.geojson}
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
          dates={geojsonList.map((item) => item.date)}
          selectedDate={selectedDate}
          setSelectedDate={setSelectedDate}
        />
        <LayerSelector selectedLayer={selectedLayer} setSelectedLayer={setSelectedLayer} />
      </div>
    </div>
  );
}

export default App;
