import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";

const RegisterForm = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    username: "",
    email: "",
    full_name: "",
    password: "",
  });

  const [notification, setNotification] = useState({ message: "", type: "" });

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post("http://localhost:8000/api/auth/register", formData);
      setNotification({
        message: "Usuario registrado correctamente",
        type: "success",
      });
      navigate("/");
    } catch (err) {
      const errorMsg =
        err.response?.data?.detail || "Error al registrar el usuario";
      setNotification({ message: errorMsg, type: "error" });
    }
  };

  const alertClass =
    notification.type === "success"
      ? "alert alert-success"
      : notification.type === "error"
      ? "alert alert-danger"
      : "";

  return (
    <div
      className="d-flex align-items-center justify-content-center min-vh-100"
      style={{
        background:
          "linear-gradient(135deg, rgba(30,144,255,0.15) 0%, rgba(46,213,115,0.15) 100%)",
      }}
    >
      <div className="card shadow-lg rounded-4 p-4 p-md-5" style={{ maxWidth: "500px", width: "100%" }}>
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

        <h2 className="h4 text-center mb-4">Sign up</h2>

        {notification.message && (
          <div className={`${alertClass} py-2`} role="alert">
            {notification.message}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          {/* Usuario */}
          <div className="mb-3">
            <label className="form-label">Username</label>
            <div className="input-group">
              <span className="input-group-text">
                <i className="bi bi-person"></i>
              </span>
              <input
                type="text"
                className="form-control"
                name="username"
                onChange={handleChange}
                required
              />
            </div>
          </div>

          {/* Email */}
          <div className="mb-3">
            <label className="form-label">Email</label>
            <div className="input-group">
              <span className="input-group-text">
                <i className="bi bi-envelope"></i>
              </span>
              <input
                type="email"
                className="form-control"
                name="email"
                onChange={handleChange}
                required
              />
            </div>
          </div>

          {/* Nombre completo */}
          <div className="mb-3">
            <label className="form-label">Full name</label>
            <div className="input-group">
              <span className="input-group-text">
                <i className="bi bi-card-text"></i>
              </span>
              <input
                type="text"
                className="form-control"
                name="full_name"
                onChange={handleChange}
                required
              />
            </div>
          </div>

          {/* Password */}
          <div className="mb-4">
            <label className="form-label">Password</label>
            <div className="input-group">
              <span className="input-group-text">
                <i className="bi bi-lock"></i>
              </span>
              <input
                type="password"
                className="form-control"
                name="password"
                onChange={handleChange}
                required
              />
            </div>
          </div>

          <button type="submit" className="btn btn-primary w-100 py-2 fw-semibold">
            Create account
          </button>
        </form>
      </div>
    </div>
  );
};

export default RegisterForm;