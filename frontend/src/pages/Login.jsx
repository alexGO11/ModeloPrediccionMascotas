import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [user, setUser] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await login(user, password);
      navigate("/MapPage");
    } catch (err) {
      if (err?.response?.data?.detail) {
        setError(err.response.data.detail);
      } else {
        setError("Error al iniciar sesión. Inténtalo de nuevo.");
      }
    }
  };

  return (
    <div
      className="d-flex align-items-center justify-content-center min-vh-100"
      style={{
        background:
          "linear-gradient(135deg, rgba(30,144,255,0.15) 0%, rgba(46,213,115,0.15) 100%)",
      }}
    >
      <div className="card shadow-lg rounded-4 p-4 p-md-5" style={{ width: "100%", maxWidth: 420 }}>
        {/* Branding */}
        <div className="d-flex flex-column align-items-center mb-3">
          <div className="d-flex align-items-center gap-2">
            <h1 className="h4 m-0 fw-bold text-primary">Disease Pet Scan</h1>
            {/* Pin */}
            <svg width="22" height="22" viewBox="0 0 24 24" fill="#16a34a" aria-hidden="true">
              <path d="M12 2C8.7 2 6 4.7 6 8c0 4.5 6 12 6 12s6-7.5 6-12c0-3.3-2.7-6-6-6Zm0 8.5A2.5 2.5 0 1 1 12 5a2.5 2.5 0 0 1 0 5Z"/>
            </svg>
          </div>
        </div>

        <h2 className="h4 text-center mb-4">Sign in</h2>

        {error && (
          <div className="alert alert-danger py-2" role="alert">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="needs-validation" noValidate>
          {/* Usuario */}
          <div className="mb-3">
            <label className="form-label">Username</label>
            <div className="input-group">
              <span className="input-group-text">
                <i className="bi bi-person"></i>
              </span>
              <input
                type="text"
                value={user}
                onChange={(e) => setUser(e.target.value)}
                className="form-control"
                placeholder="username"
                required
              />
            </div>
          </div>

          {/* Password */}
          <div className="mb-2">
            <label className="form-label">Password</label>
            <div className="input-group">
              <span className="input-group-text">
                <i className="bi bi-lock"></i>
              </span>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="form-control"
                placeholder="••••••••"
                required
              />
            </div>
          </div>

          <button type="submit" className="btn btn-primary w-100 py-2 fw-semibold">
            Enter
          </button>
        </form>

        <hr className="my-4" />

        <div className="text-center">
          <span className="text-muted me-2">Don't have an account?</span>
          <button
            className="btn btn-outline-secondary"
            onClick={() => navigate("/register")}
          >
            Sign up
          </button>
        </div>
      </div>
    </div>
  );
}