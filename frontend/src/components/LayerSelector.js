const LayerSelector = ({ selectedLayer, setSelectedLayer }) => {
    return (
      <div style={{ display: "flex", flexDirection: "column" }}>
        <label style={{ marginBottom: "5px" }}>Selecciona capa:</label>
        <select
          value={selectedLayer}
          onChange={(e) => setSelectedLayer(e.target.value)}
          style={{ padding: "5px", borderRadius: "6px", border: "1px solid #ccc" }}
        >
          <option value="z_value">Heatmap</option>
          <option value="temperatura">Temperatura</option>
          {/* Agrega más capas aquí si las tienes */}
        </select>
      </div>
    );
  };
  
  export default LayerSelector;