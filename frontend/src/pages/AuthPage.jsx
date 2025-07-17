import LoginForm from '../components/LoginForm';
import RegisterForm from '../components/RegisterForm';
import '../styles/AuthPage.css'; // opcional para estilos

export default function AuthPage({ onLogin }) {
  return (
    <div className="auth-page">
      <h1>Bienvenido</h1>
      <div className="forms">
        <LoginForm onLogin={onLogin} />
        <RegisterForm />
      </div>
    </div>
  );
}