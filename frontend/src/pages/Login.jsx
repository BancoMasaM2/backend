import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { api } from '../services/api';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      const data = await api.login(email, password);
      localStorage.setItem('usuario_id', data.usuario_id);
      localStorage.setItem('nombre', data.nombre);
      localStorage.setItem('alias', data.alias);
      navigate('/dashboard');
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div style={styles.wrapper}>
      <div style={styles.card}>
        <h2 style={styles.title}>Iniciar sesión</h2>
        <p style={styles.subtitle}>Ingresá a GCDR Online</p>
        {error && <p style={styles.error}>{error}</p>}
        <form onSubmit={handleSubmit} style={styles.form}>
          <input
            type="email" placeholder="Email"
            value={email} onChange={(e) => setEmail(e.target.value)}
            style={styles.input} required
          />
          <input
            type="password" placeholder="Contraseña"
            value={password} onChange={(e) => setPassword(e.target.value)}
            style={styles.input} required
          />
          <button type="submit" style={styles.btn}>Ingresar</button>
        </form>
        <p style={styles.footerText}>
          ¿No tenés cuenta? <Link to="/registro">Registrate</Link>
        </p>
      </div>
    </div>
  );
}

const styles = {
  wrapper: { display: 'flex', justifyContent: 'center', marginTop: 80 },
  card: {
    width: 360, padding: 32,
    border: '1px solid #e2e8f0', borderRadius: 12,
    background: '#fff',
  },
  title: { fontSize: 22, fontWeight: 700, color: '#1e293b', marginBottom: 4 },
  subtitle: { fontSize: 14, color: '#64748b', marginBottom: 24 },
  error: { fontSize: 13, color: '#dc2626', marginBottom: 12, padding: '8px 12px', background: '#fef2f2', borderRadius: 6 },
  form: { display: 'flex', flexDirection: 'column', gap: 12 },
  input: {
    padding: '10px 14px', border: '1px solid #e2e8f0', borderRadius: 6,
    fontSize: 14, fontFamily: "'Inter', sans-serif", outline: 'none',
  },
  btn: {
    padding: '10px 20px', background: '#2563eb', color: '#fff',
    border: 'none', borderRadius: 6, cursor: 'pointer',
    fontSize: 14, fontWeight: 500, fontFamily: "'Inter', sans-serif",
  },
  footerText: { fontSize: 13, color: '#64748b', textAlign: 'center', marginTop: 20 },
};
