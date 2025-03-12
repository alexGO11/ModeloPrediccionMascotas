import React, { useState } from "react";

const TimeIntervalSelector = ({ interval, setInterval }) => {
  const [tempInterval, setTempInterval] = useState(interval); // Estado temporal para el input

  const handleKeyDown = (e) => {
    if (e.key === "Enter") {
      setInterval(tempInterval); // Solo actualiza cuando se presiona Enter
    }
  };

  return (
    <div>
      <label>Intervalo de tiempo (días):</label>
      <input
        type="number"
        min="30"
        max="365"
        value={tempInterval}
        onChange={(e) => setTempInterval(Number(e.target.value))}
        onKeyDown={handleKeyDown} // Ejecuta solo cuando se presiona Enter
      />
    </div>
  );
};

export default TimeIntervalSelector;
