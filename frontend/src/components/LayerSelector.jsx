import React, { useState } from "react";

{/* Layer selector component to choose which layers to display on the map */}
const LayerSelector = ({ selectedLayers, setSelectedLayers, offsetHuman, setOffsetHuman, offsetTemperature, setOffsetTemperature }) => {
  const handleCheckboxChange = (layer) => {
    if (selectedLayers.includes(layer)) {
      setSelectedLayers(selectedLayers.filter((l) => l !== layer));
    } else {
      setSelectedLayers([...selectedLayers, layer]);
    }
  };
  const [humanInputValue, setHumanInputValue] = useState(offsetHuman);
  const [temperatureInputValue, setTemperatureInputValue] = useState(offsetTemperature);

  const handleHumanKeyDown = (e) => {
    if (e.key === "Enter") {
      setOffsetHuman(Number(humanInputValue));
    }
  };

  const handleTemperatureKeyDown = (e) => {
    if (e.key === "Enter") {
      setOffsetTemperature(Number(temperatureInputValue));
    }
  };

  return (
    <div style={{ display: "flex", flexDirection: "column" }}>
      <label>
        <input
          type="checkbox"
          defaultChecked
          checked={selectedLayers.includes("human")}
          onChange={() => handleCheckboxChange("human")}
        /> Human
        <div style={{ display: "flex", flexDirection: "column" }}>
          <label style={{ marginBottom: "5px" }}>
            Offset Human (days):
            <input
              type="number"
              min="-30"
              max="365"
              value={humanInputValue}
              onChange={(e) => setHumanInputValue(e.target.value)}
              onKeyDown={handleHumanKeyDown}
              style={{ padding: "5px", borderRadius: "6px", border: "1px solid #ccc" }}
            />
          </label>
        </div>
      </label>

      <label>
        <input
          type="checkbox"
          defaultChecked
          checked={selectedLayers.includes("temperature")}
          onChange={() => handleCheckboxChange("temperature")}
        /> Temperature
        <div style={{ display: "flex", flexDirection: "column" }}>
          <label style={{ marginBottom: "5px" }}>
            Offset Temperature (days):
            <input
              type="number"
              min="-30"
              max="365"
              value={temperatureInputValue}
              onChange={(e) => setTemperatureInputValue(e.target.value)}
              onKeyDown={handleTemperatureKeyDown}
              style={{ padding: "5px", borderRadius: "6px", border: "1px solid #ccc" }}
            />
          </label>
        </div>
      </label>
    </div>
  );
};

export default LayerSelector;