import { useState } from 'react';
import { api } from '../services/api';

export default function Pagos() {
  const [monto, setMonto] = useState('');
  const [descripcion, setDescripcion] = useState('');
  const [mensaje, setMensaje] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const usuarioId = Number(localStorage.getItem('usuario_id'));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMensaje('');
    setError('');
    setLoading(true);
    try {
      const res = await api.pagar(usuarioId, Number(monto), descripcion);
      setMensaje(`Pago exitoso. ID: ${res.detalle.pago_id}`);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h2 style={styles.title}>Pagos</h2>
      {mensaje && <p style={styles.success}>{mensaje}</p>}
      {error && <p style={styles.error}>{error}</p>}
      <form onSubmit={handleSubmit} style={styles.form}>
        <input type="number" step="0.01" min="0.01" placeholder="Monto ARS"
          value={monto} onChange={(e) => setMonto(e.target.value)}
          style={styles.input} required
        />
        <input placeholder="Descripción (opcional)"
          value={descripcion} onChange={(e) => setDescripcion(e.target.value)}
          style={styles.input}
        />
        <button type="submit" disabled={loading} style={styles.btn}>
          {loading ? 'Procesando...' : 'Pagar'}
        </button>
      </form>
    </div>
  );
}

const styles = {
  title: { fontSize: 22, fontWeight: 700, color: '#1e293b', marginBottom: 20 },
  success: {
    fontSize: 13, color: '#16a34a', padding: '10px 14px', background: '#f0fdf4',
    borderRadius: 6, marginBottom: 16,
  },
  error: {
    fontSize: 13, color: '#dc2626', padding: '10px 14px', background: '#fef2f2',
    borderRadius: 6, marginBottom: 16,
  },
  form: { display: 'flex', flexDirection: 'column', gap: 12, maxWidth: 360 },
  input: {
    padding: '10px 14px', border: '1px solid #e2e8f0', borderRadius: 6,
    fontSize: 14, fontFamily: "'Inter', sans-serif", outline: 'none',
  },
  btn: {
    padding: '10px 20px', background: '#2563eb', color: '#fff',
    border: 'none', borderRadius: 6, cursor: 'pointer',
    fontSize: 14, fontWeight: 500, fontFamily: "'Inter', sans-serif",
  },
};
