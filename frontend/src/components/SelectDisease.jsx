const DiseaseSelector = ({ selectedDisease, setSelectedDisease }) => {
    return (
      <div style={{ display: "flex", flexDirection: "column" }}>
        <select
          value={selectedDisease}
          onChange={(e) => setSelectedDisease(e.target.value)}
          style={{ padding: "5px", borderRadius: "6px", border: "1px solid #ccc" }}
        >
          <option value="Leishmania">Leishmania</option>
          <option value="Giardia">Giardia</option>
        </select>
      </div>
    );
  };
  
  export default DiseaseSelector;