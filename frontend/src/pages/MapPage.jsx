
import axios from "axios";
import { useState } from "react";
import Heatmap from "../components/Map";
import SidePanel from "../components/SidePanel";


export default function MapPage() {
  const [startDate, setStartDate] = useState(new Date().toISOString().slice(0, 10));
  const [interval, setInterval] = useState(365);
  const [offsetHuman, setOffsetHuman] = useState(0);
  const [offsetTemperature, setOffsetTemperature] = useState(0);
  const [geojsonList, setGeojsonList] = useState([]);
  const [selectedLayers, setSelectedLayers] = useState(["human", "temperature"]);
  const [selectedDate, setSelectedDate] = useState(startDate);
  const [selectedDisease, setSelectedDisease] = useState("Leishmania");
  const [currInterval, setCurrInterval] = useState(0);
  const [loading, setLoading] = useState(false);

  const fetchData = async () => {
    try {
      setCurrInterval(Number(interval));

      const api = axios.create({
        baseURL: process.env.REACT_APP_API_URL || "/api", 
        headers: { "Content-Type": "application/json" },
        withCredentials: false,
      });


      const [filteredRes, aemetRes, humanRes] = await Promise.all([
        api.post("/test/filtered", {
          interval,
          disease: selectedDisease,
        }),
        api.post("/aemet/get_data", {
          interval,
          offset: offsetTemperature,
        }),
        api.post("/human/get_human_data", {
          interval,
          disease: selectedDisease,
          offset: offsetHuman,
        }),
      ]);

      // Procesar los datos añadiendo la fuente correspondiente
      const processedFiltered = filteredRes.data.map((item) => ({
        ...item,
        source: "filtered",
      }));

      const processedAemet = aemetRes.data.map((item) => ({
        ...item,
        source: "aemet",
      }));

      const processedHuman = humanRes.data.map((item) => ({
        ...item,
        source: "human",
      }));

      // Guardar todo en el estado
      setGeojsonList([...processedFiltered, ...processedAemet, ...processedHuman]);
    } catch (err) {
      console.error("Error al cargar datos:", err);
    }
  };

  return (
      <div style={{ width: "100vw", height: "100vh", position: "relative" }}>
          {/* renderiza el mapa */}
          <Heatmap
            diseaseData={geojsonList.find((item) => item.date === selectedDate && item.source === "filtered")?.geojson}
            aemetData={geojsonList.find((item) => item.date === selectedDate && item.source === "aemet")?.geojson}
            humanData={geojsonList.find((item) => item.date === selectedDate && item.source === "human")?.geojson}
            selectedLayers={selectedLayers}
          />

        <SidePanel
          interval={interval}
          setInterval={setInterval}
          selectedDate={selectedDate}
          setSelectedDate={setSelectedDate}
          geojsonList={geojsonList}
          selectedLayers={selectedLayers}
          setSelectedLayers={setSelectedLayers}
          offsetHuman={offsetHuman}
          setOffsetHuman={setOffsetHuman}
          offsetTemperature={offsetTemperature}
          setOffsetTemperature={setOffsetTemperature}
          selectedDisease={selectedDisease}
          setSelectedDisease={setSelectedDisease}
          fetchData={fetchData}
          currInterval={currInterval}
        />
        
        {loading && (
          <div
            style={{
              position: "absolute",
              top: 0,
              left: 0,
              width: "100%",
              height: "100%",
              backgroundColor: "rgba(255, 255, 255, 0.3)",
              backdropFilter: "blur(6px)",
              WebkitBackdropFilter: "blur(6px)",
              display: "flex",
              justifyContent: "center",
              alignItems: "center",
              zIndex: 9999,
            }}
          >
            <div
              style={{
                width: "60px",
                height: "60px",
                border: "6px solid rgba(0, 0, 0, 0.2)",
                borderTop: "6px solid #007bff",
                borderRadius: "50%",
                animation: "spin 1s linear infinite",
              }}
            />
          </div>
        )}
    </div>
  );

}
