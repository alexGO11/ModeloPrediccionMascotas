import React, { useEffect, useState } from "react";
import Heatmap from "./components/map";
import TimeIntervalSelector from "./components/TimeIntervalSelector";
import TimeSlider from "./components/TimeSlider";

function App() {
  const [startDate, setStartDate] = useState("2020-07-20");
  const [interval, setInterval] = useState(365);
  const [desease, setDesease] = useState("Leishmania");
  const [geojsonList, setGeojsonList] = useState([]);
  const [selectedDate, setSelectedDate] = useState(startDate);
  const [loading, setLoading] = useState(false); // Estado de carga

  useEffect(() => {
    setLoading(true); // Comienza la carga

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
        console.log("Datos recibidos:", data);
        setGeojsonList(data);
        setSelectedDate(data[0]?.date);
        setLoading(false); // Finaliza la carga cuando llegan los datos
      })
      .catch((error) => {
        console.error("Error:", error);
        setLoading(false); // Finaliza la carga en caso de error
      });
  }, [startDate, interval, desease]);

  console.log("Enviando JSON a la API:", {
    start_date: startDate,
    end_date: "2025-12-31",
    interval: interval,
    desease: desease,
  });
  
  return (
    <div>
      <TimeIntervalSelector interval={interval} setInterval={setInterval} />
      <TimeSlider
        dates={geojsonList.map((item) => item.date)}
        selectedDate={selectedDate}
        setSelectedDate={setSelectedDate}
      />

      {/* Mensaje de carga mientras los datos se están obteniendo */}
      {loading ? (
        <p>Cargando datos...</p>
      ) : (
        <Heatmap geojsonData={geojsonList.find((item) => item.date === selectedDate)?.geojson} />
      )}
    </div>
  );
}

export default App;
