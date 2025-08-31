const DiseaseSelector = ({ selectedDisease, setSelectedDisease }) => {
    return (
      <div style={{ display: "flex", flexDirection: "column" }}>
        <label style={{ marginBottom: "5px" }}>Select disease:</label>
        <select
          value={selectedDisease}
          onChange={(e) => setSelectedDisease(e.target.value)}
          style={{ padding: "5px", borderRadius: "6px", border: "1px solid #ccc" }}
        >
          <option value="z_value">Leishmania</option>
          <option value="temperatura">Giardia</option>
        </select>
      </div>
    );
  };
  
  export default DiseaseSelector;