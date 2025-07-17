import { useState } from 'react';

export default function LoginForm({ onLogin }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  async function handleLogin(e) {
    e.preventDefault();
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);

    const res = await fetch('http://localhost:8000/token', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData,
    });

    const data = await res.json();
    if (res.ok) {
      localStorage.setItem('token', data.access_token);
      onLogin();
    } else {
      alert('Login failed: ' + data.detail);
    }
  }

  return (
    <form onSubmit={handleLogin}>
      <h2>Iniciar Sesión</h2>
      <input placeholder="Usuario" value={username} onChange={(e) => setUsername(e.target.value)} />
      <input placeholder="Contraseña" type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
      <button type="submit">Entrar</button>
    </form>
  );
}
