import { useState, useEffect, useRef } from "react";

const TimeSlider = ({ dates, selectedDate, setSelectedDate }) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const intervalRef = useRef(null);

  const currentIndex = dates.indexOf(selectedDate);

  // Handle automatic date advancement
  useEffect(() => {
    if (isPlaying) {
      intervalRef.current = setInterval(() => {
        setSelectedDate((prevDate) => {
          const currentIndex = dates.indexOf(prevDate);
          const nextIndex = currentIndex + 1;

          // Stops at the end
          if (nextIndex >= dates.length) {
            clearInterval(intervalRef.current);
            setIsPlaying(false);
            return prevDate;
          }
          return dates[nextIndex];
        });
      }, 500); // Speed of advancement (500ms)
    } else {
      clearInterval(intervalRef.current);
    }

    return () => clearInterval(intervalRef.current);
  }, [isPlaying, dates, setSelectedDate]);

  // Handle manual change on the slider
  const handleSliderChange = (e) => {
    const newIndex = parseInt(e.target.value);
    setSelectedDate(dates[newIndex]);
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>

      {/* Slider */}
      <input
        type="range"
        min={0}
        max={dates.length - 1}
        value={currentIndex}
        onChange={handleSliderChange}
        style={{ width: "100%" }}
      />

      <div style={{ textAlign: "center", fontWeight: "bold" }}>
        {selectedDate}
      </div>

      {/* Automatic time advance button */}
      <button
        onClick={() => setIsPlaying(!isPlaying)}
        style={{
          marginTop: "5px",
          padding: "6px 12px",
          border: "none",
          borderRadius: "6px",
          backgroundColor: isPlaying ? "#dc3545" : "#007bff",
          color: "white",
          cursor: "pointer",
          fontWeight: "bold",
          transition: "background-color 0.3s ease"
        }}
      >
        {isPlaying ? "⏸ Pause" : "▶ Play"}
      </button>
    </div>
  );
};

export default TimeSlider;