import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "./context/AuthContext";
import Login from "./pages/Login";
import Register from "./pages/Register";
import MapPage from "./pages/MapPage";

// Componente para proteger rutas privadas
function PrivateRoute({ children }) {
  const { token } = useAuth();
  return token ? children : <Navigate to="/" />;
}

export default function App() {
  return (
    <AuthProvider>  {/*Provee autenticación*/}
      <BrowserRouter> {/*Rutas que tiene la página*/}
        <Routes>
          <Route path="/" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route
            path="/MapPage"
            element={ 
              <PrivateRoute> {/*Protege la ruta de MapPage si no estas autenticado*/}
                <MapPage />
              </PrivateRoute>
            }
          />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
