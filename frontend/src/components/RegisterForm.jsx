import { useState } from 'react';

export default function RegisterForm() {
  const [form, setForm] = useState({
    username: '',
    email: '',
    full_name: '',
    password: '',
  });

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  async function handleRegister(e) {
    e.preventDefault();
    const res = await fetch('http://localhost:8000/users', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form),
    });

    const data = await res.json();
    if (res.ok) {
      alert('Usuario creado correctamente');
    } else {
      alert('Error: ' + data.detail || JSON.stringify(data));
    }
  }

  return (
    <form onSubmit={handleRegister}>
      <h2>Registrarse</h2>
      <input name="username" placeholder="Usuario" onChange={handleChange} />
      <input name="email" placeholder="Email" onChange={handleChange} />
      <input name="full_name" placeholder="Nombre completo" onChange={handleChange} />
      <input name="password" placeholder="Contraseña" type="password" onChange={handleChange} />
      <button type="submit">Crear cuenta</button>
    </form>
  );
}
