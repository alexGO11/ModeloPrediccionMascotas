import "../styles/LoadingScreen.css";

export default function LoadingScreen() {
  return (
    <div className="loading-overlay">
      <div className="spinner"></div>
      <p>Cargando datos...</p>
    </div>
  );
}