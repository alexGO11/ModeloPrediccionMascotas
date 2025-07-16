import React, { useState } from "react";


const LayerSelector = ({ selectedLayers, setSelectedLayers, offsetHuman, setOffsetHuman, offsetTemperature, setOffsetTemperature }) => {
  const handleCheckboxChange = (layer) => {
    if (selectedLayers.includes(layer)) {
      setSelectedLayers(selectedLayers.filter((l) => l !== layer));
    } else {
      setSelectedLayers([...selectedLayers, layer]);
    }
  };
  const [inputValue, setInputValue] = useState(offsetHuman, offsetTemperature);
  const handleKeyDown = (e) => {
    if (e.key === "Enter") {
      setOffsetHuman(Number(offsetHuman));
      setOffsetTemperature(Number(offsetTemperature));
    }
  };

  return (
    <div style={{ display: "flex", flexDirection: "column" }}>
      <label><input
        type="checkbox"
        defaultChecked
        checked={selectedLayers.includes("human")}
        onChange={() => handleCheckboxChange("human")}
      /> Human
          <div style={{ display: "flex", flexDirection: "column" }}>
            <label style={{ marginBottom: "5px" }}>Offset Human (days): 
              <input
                type="number"
                min="-30"
                max="365"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={handleKeyDown}
                style={{ padding: "5px", borderRadius: "6px", border: "1px solid #ccc" }}
              />
              </label>
        </div>
      </label>



      <label><input
        type="checkbox"
        defaultChecked
        checked={selectedLayers.includes("temperature")}
        onChange={() => handleCheckboxChange("temperature")}
      /> Temperature
        <div style={{ display: "flex", flexDirection: "column" }}>
            <label style={{ marginBottom: "5px" }}>Offset Temperature (days): 
              <input
                type="number"
                min="-30"
                max="365"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={handleKeyDown}
                style={{ padding: "5px", borderRadius: "6px", border: "1px solid #ccc" }}
              />
              </label>
        </div>
      </label>
    </div>
  );
};

export default LayerSelector;