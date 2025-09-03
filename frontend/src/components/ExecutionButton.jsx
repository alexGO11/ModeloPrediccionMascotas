import React, { useState } from "react";
import LoadingScreen from "../pages/Loading";


const ExecutionButton = ({ fetchData, currInterval, interval }) => {
  const [loading, setLoading] = useState(false);
  
  // function to manage execution button
  const handleClick = async () => {
    console.log(`Current Interval: ${currInterval}, Selected Interval: ${interval}`);
    if(currInterval !== interval) {
      setLoading(true);
      await fetchData();
      setLoading(false);
    }
  };

  // Show loading screen if loading
  if (loading) return <LoadingScreen />;

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
      {loading ? "Loading..." : "Load data"}
    </button>
  );
}

export default ExecutionButton;