const TimeSlider = ({ dates, selectedDate, setSelectedDate }) => {
  return (
    <div style={{ display: "flex", flexDirection: "column" }}>
      <label style={{ marginBottom: "5px" }}>Selected date:</label>
      <input
        type="range"
        min={0}
        max={dates.length - 1}
        value={dates.indexOf(selectedDate)}
        onChange={(e) => setSelectedDate(dates[e.target.value])}
        style={{ width: "100%" }}
      />
      <div style={{ textAlign: "center", marginTop: "5px", fontWeight: "bold" }}>
        {selectedDate}
      </div>
    </div>
  );
};

export default TimeSlider;