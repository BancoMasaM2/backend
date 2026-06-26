import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { api } from '../services/api';

export default function Registro() {
  const [step, setStep] = useState('form');
  const [form, setForm] = useState({ nombre: '', email: '', password: '' });
  const [codigo, setCodigo] = useState('');
  const [error, setError] = useState('');
  const [mensaje, setMensaje] = useState('');
  const navigate = useNavigate();

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleRegister = async (e) => {
    e.preventDefault();
    setError('');
    try {
      const res = await api.registro(form.nombre, form.email, form.password);
      setMensaje(res.mensaje);
      setStep('verificar');
    } catch (err) {
      setError(err.message);
    }
  };

  const handleVerify = async (e) => {
    e.preventDefault();
    setError('');
    try {
      await api.verificarCodigo(form.email, codigo);
      navigate('/login');
    } catch (err) {
      setError(err.message);
    }
  };

  const handleReenviar = async () => {
    setError('');
    try {
      const res = await api.reenviarCodigo(form.email);
      setMensaje(res.mensaje);
    } catch (err) {
      setError(err.message);
    }
  };

  if (step === 'verificar') {
    return (
      <div style={styles.wrapper}>
        <div style={styles.card}>
          <h2 style={styles.title}>Verificar email</h2>
          {mensaje && <p style={styles.success}>{mensaje}</p>}
          {error && <p style={styles.error}>{error}</p>}
          <form onSubmit={handleVerify} style={styles.form}>
            <input placeholder="Código de verificación" value={codigo}
              onChange={(e) => setCodigo(e.target.value)}
              style={styles.input} maxLength={6} required
            />
            <button type="submit" style={styles.btn}>Verificar</button>
            <button type="button" onClick={handleReenviar} style={styles.btnOutline}>Reenviar código</button>
          </form>
          <p style={styles.footerText}>¿Ya tenés cuenta? <Link to="/login">Iniciá sesión</Link></p>
        </div>
      </div>
    );
  }

  return (
    <div style={styles.wrapper}>
      <div style={styles.card}>
        <h2 style={styles.title}>Crear cuenta</h2>
        <p style={styles.subtitle}>Abrí tu cuenta en Banco GCDR</p>
        {error && <p style={styles.error}>{error}</p>}
        <form onSubmit={handleRegister} style={styles.form}>
          <input name="nombre" placeholder="Nombre" value={form.nombre} onChange={handleChange} style={styles.input} required />
          <input name="email" type="email" placeholder="Email" value={form.email} onChange={handleChange} style={styles.input} required />
          <input name="password" type="password" placeholder="Contraseña" value={form.password} onChange={handleChange} style={styles.input} required />
          <button type="submit" style={styles.btn}>Registrarse</button>
        </form>
        <p style={styles.footerText}>¿Ya tenés cuenta? <Link to="/login">Iniciá sesión</Link></p>
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
  success: { fontSize: 13, color: '#16a34a', marginBottom: 12, padding: '8px 12px', background: '#f0fdf4', borderRadius: 6 },
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
  btnOutline: {
    padding: '10px 20px', background: '#fff', color: '#1e293b',
    border: '1px solid #e2e8f0', borderRadius: 6, cursor: 'pointer',
    fontSize: 14, fontWeight: 500, fontFamily: "'Inter', sans-serif",
  },
  footerText: { fontSize: 13, color: '#64748b', textAlign: 'center', marginTop: 20 },
};
