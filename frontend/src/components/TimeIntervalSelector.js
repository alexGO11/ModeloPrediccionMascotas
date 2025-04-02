import React, { useState } from "react";


const TimeIntervalSelector = ({ interval, setInterval }) => {
  const [inputValue, setInputValue] = useState(interval);

  const handleKeyDown = (e) => {
    if (e.key === "Enter") {
      setInterval(Number(inputValue));
    }
  };

  return (
    <div style={{ display: "flex", flexDirection: "column" }}>
      <label style={{ marginBottom: "5px" }}>Intervalo de tiempo (días):</label>
      <input
        type="number"
        min="30"
        max="365"
        value={inputValue}
        onChange={(e) => setInputValue(e.target.value)}
        onKeyDown={handleKeyDown}
        style={{ padding: "5px", borderRadius: "6px", border: "1px solid #ccc" }}
      />
    </div>
  );
};

export default TimeIntervalSelector;