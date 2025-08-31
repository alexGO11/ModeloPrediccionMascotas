import React, { useState } from 'react';
import axios from 'axios';

const RegisterForm = () => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    full_name: '',
    password: ''
  });

  const [message, setMessage] = useState('');

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const res = await axios.post('http://localhost:8000/api/auth/register', formData);
      setMessage('Usuario registrado correctamente');
    } catch (err) {
      if (err.response && err.response.data && err.response.data.detail) {
        setMessage(err.response.data.detail);
      } else {
        setMessage('Error al registrar el usuario');
      }
    }
  };

  return (
    <div className="register-background">
      <div className="container d-flex align-items-center justify-content-center min-vh-100">
        <div className="card p-4 shadow-lg" style={{ maxWidth: "500px", width: "100%" }}>
          <h2 className="text-center mb-4">Registro</h2>

          {message && <div className="alert alert-info">{message}</div>}

          <form onSubmit={handleSubmit}>
            <div className="mb-3">
              <label className="form-label">Nombre de usuario</label>
              <input
                type="text"
                className="form-control"
                name="username"
                onChange={handleChange}
                required
              />
            </div>

            <div className="mb-3">
              <label className="form-label">Correo electrónico</label>
              <input
                type="email"
                className="form-control"
                name="email"
                onChange={handleChange}
                required
              />
            </div>

            <div className="mb-3">
              <label className="form-label">Nombre completo</label>
              <input
                type="text"
                className="form-control"
                name="full_name"
                onChange={handleChange}
                required
              />
            </div>

            <div className="mb-3">
              <label className="form-label">Contraseña</label>
              <input
                type="password"
                className="form-control"
                name="password"
                onChange={handleChange}
                required
              />
            </div>

            <button type="submit" className="btn btn-primary w-100">
              Registrarse
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default RegisterForm;
