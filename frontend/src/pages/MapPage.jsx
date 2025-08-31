import React, { useEffect, useState } from "react";
import LayerSelector from "../components/LayerSelector";
import TimeIntervalSelector from "../components/TimeIntervalSelector";
import TimeSlider from "../components/TimeSlider";
import Heatmap from "../components/map";
import DiseaseSelector from "../components/selectDisease";
import ExecutionButton from "../components/executionButton";

export default function MapPage() {
  // State variables for managing user selections and data
  const [startDate, setStartDate] = useState(new Date().toISOString().slice(0, 10));
  const [interval, setInterval] = useState(365);
  const [offsetHuman, setOffsetHuman] = useState(0);
  const [offsetTemperature, setOffsetTemperature] = useState(0);
  const [disease, setdisease] = useState("Leishmania");
  const [geojsonList, setGeojsonList] = useState([]);
  const [selectedLayers, setSelectedLayers] = useState([]);
  const [selectedDate, setSelectedDate] = useState(startDate);
  const [selectedDisease, setSelectedDisease] = useState("Leishmania");
  const [currInterval, setCurrInterval] = useState(0);

  const fetchData = () => {
    setCurrInterval(Number(interval));
    // Fetch filtered data based on user selections
    const filteredRequest = fetch("http://localhost:8000/api/test/filtered", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        start_date: "2022-01-01",
        interval: interval,
        disease: selectedDisease,
      }),
    }).then((res) => res.json());

    // Adjust start date based on temperature offset
    const startDateObj = new Date("2022-01-01");
    startDateObj.setDate(startDateObj.getDate() + offsetTemperature);
    const offsetStartDate = startDateObj.toISOString().slice(0, 10);

    // Fetch AEMET data
    const aemetRequest = fetch("http://localhost:8000/api/aemet/get_data", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
      start_date: offsetStartDate,
      interval: interval,
      }),
    }).then((res) => res.json());

    // Fetch human data
    const humanRequest = fetch("http://localhost:8000/api/human/get_human_data", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
      interval: interval,
      disease: selectedDisease,
      }),
    }).then((res) => res.json());

    // Combine all fetched data
    Promise.all([filteredRequest, aemetRequest, humanRequest]).then(([filteredData, aemetData, humanData]) => {
      const processedFiltered = filteredData.map((item) => ({
        ...item,
        source: "filtered",
      }));

      const processedAemet = aemetData.map((item) => ({
        ...item,
        source: "aemet",
      }));

      const processedHuman = humanData.map((item) => ({
        ...item,
        source: "human",
      }));

      // Update state with combined data
      setGeojsonList([...processedFiltered, ...processedAemet, ...processedHuman]);
    });
  };

  return (
      <div style={{ width: "100vw", height: "100vh", position: "relative" }}>
          {/* Render the heatmap with the fetched data */}
          <Heatmap
            diseaseData={geojsonList.find((item) => item.date === selectedDate && item.source === "filtered")?.geojson}
            aemetData={geojsonList.find((item) => item.date === selectedDate && item.source === "aemet")?.geojson}
            humanData={geojsonList.find((item) => item.date === selectedDate && item.source === "human")?.geojson}
            selectedLayers={selectedLayers}
          />

        {/* Container for controls like sliders and selectors */}
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
          {/* Render the rest of the components */}
        <TimeIntervalSelector interval={interval} setInterval={setInterval} />
        <TimeSlider
          dates={[...new Set(geojsonList.map((item) => item.date))].sort()}
          selectedDate={selectedDate}
          setSelectedDate={setSelectedDate}
        />
        <LayerSelector selectedLayers={selectedLayers} setSelectedLayers={setSelectedLayers} offsetHuman={offsetHuman} setOffsetHuman={offsetHuman} offsetTemperature={offsetHuman} setOffsetTemperature={setOffsetTemperature} />
        <DiseaseSelector selectedDisease={selectedDisease} setSelectedDisease={setSelectedDisease} />
        <ExecutionButton fetchData={fetchData} currInterval={currInterval} interval={interval} />
      </div>
    </div>
  );
}
