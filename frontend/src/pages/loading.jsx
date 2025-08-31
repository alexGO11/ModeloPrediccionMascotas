import "../styles/LoadingScreen.css";

export default function LoadingScreen() {
  // Render a loading overlay with a spinner and a loading message
  return (
    <div className="loading-overlay">
      <div className="spinner"></div>
      <p>Cargando datos...</p>
    </div>
  );
}