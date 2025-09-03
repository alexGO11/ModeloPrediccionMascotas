import React, { useState } from "react";
import LayerSelector from "../components/LayerSelector";
import TimeIntervalSelector from "../components/TimeIntervalSelector";
import TimeSlider from "../components/TimeSlider";
import DiseaseSelector from "../components/SelectDisease";
import ExecutionButton from "../components/ExecutionButton";


export default function SidePanel({
  interval,
  setInterval,
  selectedDate,
  setSelectedDate,
  geojsonList,
  selectedLayers,
  setSelectedLayers,
  offsetHuman,
  setOffsetHuman,
  offsetTemperature,
  setOffsetTemperature,
  selectedDisease,
  setSelectedDisease,
  fetchData,
  currInterval,
}) {
  const [isCollapsed, setIsCollapsed] = useState(false);

  return (
    <div
          style={{
            position: "absolute",
            top: "20px",
            right: "20px",
            zIndex: 10,
            backgroundColor: "#fff",
            padding: "20px",
            borderRadius: "16px",
            boxShadow: "0 6px 20px rgba(0,0,0,0.25)",
            width: "300px",
            display: "flex",
            flexDirection: "column",
            gap: "18px",
            fontFamily: "'Inter', sans-serif",
          }}
        >
          {/* Título */}
          <h2
            style={{
              fontSize: "18px",
              fontWeight: "600",
              color: "#1f2937",
              marginBottom: "5px",
              textAlign: "center",
            }}
          >
            Map configuration
          </h2>

          {/* Interval selector */}
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              gap: "8px",
              background: "#f9fafb",
              padding: "10px",
              borderRadius: "10px",
              border: "1px solid #e5e7eb",
            }}
          >
            <label style={{ fontSize: "14px", fontWeight: "500", color: "#374151" }}>
              Time interval (days)
            </label>
            <TimeIntervalSelector interval={interval} setInterval={setInterval} />
          </div>

          {/* Time slider */}
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              gap: "8px",
              background: "#f9fafb",
              padding: "10px",
              borderRadius: "10px",
              border: "1px solid #e5e7eb",
            }}
          >
            <label style={{ fontSize: "14px", fontWeight: "500", color: "#374151" }}>
              Select date
            </label>
            <TimeSlider
              dates={[...new Set(geojsonList.map((item) => item.date))].sort()}
              selectedDate={selectedDate}
              setSelectedDate={setSelectedDate}
            />
          </div>

          {/* Selector de capas */}
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              gap: "8px",
              background: "#f9fafb",
              padding: "10px",
              borderRadius: "10px",
              border: "1px solid #e5e7eb",
            }}
          >
            <label style={{ fontSize: "14px", fontWeight: "500", color: "#374151" }}>
              Layer selector
            </label>
            <LayerSelector
              selectedLayers={selectedLayers}
              setSelectedLayers={setSelectedLayers}
              offsetHuman={offsetHuman}
              setOffsetHuman={setOffsetHuman}
              offsetTemperature={offsetTemperature}
              setOffsetTemperature={setOffsetTemperature}
            />
          </div>

          {/* Selector de enfermedades */}
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              gap: "8px",
              background: "#f9fafb",
              padding: "10px",
              borderRadius: "10px",
              border: "1px solid #e5e7eb",
            }}
          >
            <label style={{ fontSize: "14px", fontWeight: "500", color: "#374151" }}>
              Disease selector
            </label>
            <DiseaseSelector
              selectedDisease={selectedDisease}
              setSelectedDisease={setSelectedDisease}
            />
          </div>

          {/* Botón de ejecución */}
          <ExecutionButton fetchData={fetchData} currInterval={currInterval} interval={interval} />

      </div>
  );
}