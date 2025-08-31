import { createContext, useContext, useState, useEffect } from "react";
import axios from "axios";

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  // State to store the authentication token
  const [token, setToken] = useState(null);

  // Load the token from localStorage when the component mounts
  useEffect(() => {
    const savedToken = localStorage.getItem("token");
    if (savedToken) {
      setToken(savedToken);
    }
  }, []);

  // Function to handle user login
  const login = async (username, password) => {
    try {
      const response = await axios.post(
        "http://localhost:8000/api/auth/token",
        new URLSearchParams({
          username,
          password,
        }),
        {
          headers: {
            "Content-Type": "application/x-www-form-urlencoded",
          },
        }
      );
      // Save the token in state and localStorage
      setToken(response.data.access_token);
      localStorage.setItem("token", response.data.access_token);
    } catch (err) {
      console.error("Error al iniciar sesión:", err);
      throw err;
    }
  };

  // Function to handle user logout
  const logout = () => {
    setToken(null);
    localStorage.removeItem("token");
  };

  return (
    // Provide the authentication context to child components
    <AuthContext.Provider value={{ token, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

// Custom hook to use the authentication context
export const useAuth = () => useContext(AuthContext);
