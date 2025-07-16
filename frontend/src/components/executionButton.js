import React, { useState } from "react";

const ExecutionButton = ({ fetchData, currInterval, interval }) => {
  const [loading, setLoading] = useState(false);

  const handleClick = async () => {
    console.log(`Current Interval: ${currInterval}, Selected Interval: ${interval}`);
    if(currInterval !== interval) {
      setLoading(true);
      await fetchData();
      setLoading(false);
    }
  };

  return (
    <button
      onClick={handleClick}
      disabled={loading}
      style={{
        marginTop: "10px",
        padding: "10px 15px",
        backgroundColor: loading ? "#ccc" : "#007bff",
        color: "white",
        border: "none",
        borderRadius: "8px",
        cursor: loading ? "not-allowed" : "pointer",
        fontSize: "16px",
        fontWeight: "bold",
        transition: "background-color 0.3s ease",
      }}
      onMouseOver={(e) => {
        if (!loading) e.currentTarget.style.backgroundColor = "#0056b3";
      }}
      onMouseOut={(e) => {
        if (!loading) e.currentTarget.style.backgroundColor = "#007bff";
      }}
    >
      {loading ? "Cargando..." : "Cargar Datos"}
    </button>
  );
}

export default ExecutionButton;