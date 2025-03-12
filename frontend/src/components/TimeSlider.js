import React from "react";

const TimeSlider = ({ dates, selectedDate, setSelectedDate }) => {
  return (
    <div>
      <label>Tiempo:</label>
      <input
        type="range"
        min={0}
        max={dates.length - 1}
        value={dates.indexOf(selectedDate)}
        onChange={(e) => setSelectedDate(dates[e.target.value])}
      />
      <span>{selectedDate}</span>
    </div>
  );
};

export default TimeSlider;
