import React, { useState } from "react";

const TimeIntervalSelector = ({ interval, setInterval }) => {
  const [inputValue, setInputValue] = useState(interval);

  const handleChange = (e) => {
    const value = e.target.value;
    setInputValue(value);

    // Validamos que sea un número válido y dentro del rango permitido
    if (value === "" || isNaN(value)) return;

    const numericValue = Number(value);
    if (numericValue >= 30 && numericValue <= 365) {
      setInterval(numericValue);
    }
  };

  return (
    <div style={{ display: "flex", flexDirection: "column" }}>
      <input
        type="number"
        min="30"
        max="365"
        value={inputValue}
        onChange={handleChange}
        style={{
          padding: "5px",
          borderRadius: "6px",
          border: "1px solid #ccc",
        }}
      />
    </div>
  );
};

export default TimeIntervalSelector;
