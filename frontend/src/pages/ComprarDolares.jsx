import { useState, useEffect } from 'react';
import { api } from '../services/api';

export default function ComprarDolares() {
  const [montoARS, setMontoARS] = useState('');
  const [cotizacion, setCotizacion] = useState(null);
  const [mensaje, setMensaje] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const usuarioId = Number(localStorage.getItem('usuario_id'));

  useEffect(() => {
    api.getCotizacion('blue').then(setCotizacion).catch(() => {});
  }, []);

  const dolares = montoARS && cotizacion
    ? (Number(montoARS) / cotizacion.venta).toFixed(2)
    : '0.00';

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMensaje('');
    setError('');
    setLoading(true);
    try {
      const res = await api.convertir(usuarioId, Number(montoARS), 'ARS', 'USD');
      setMensaje(`Compra exitosa. Recibiste $${res.monto_destino} USD a una tasa de $${res.tasa} ARS/USD.`);
      setMontoARS('');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h2 style={styles.title}>Comprar dólares</h2>

      {cotizacion && (
        <div style={styles.cotizacion}>
          <span style={styles.cotLabel}>Tasa de cambio</span>
          <span style={styles.cotValor}>${Number(cotizacion.venta).toFixed(2)} ARS/USD</span>
        </div>
      )}

      {mensaje && <p style={styles.success}>{mensaje}</p>}
      {error && <p style={styles.error}>{error}</p>}

      <form onSubmit={handleSubmit} style={styles.form}>
        <label style={styles.label}>Monto en ARS</label>
        <input
          type="number" step="0.01" min="0.01"
          placeholder="Ej: 10000"
          value={montoARS}
          onChange={(e) => setMontoARS(e.target.value)}
          style={styles.input} required
        />
        {montoARS > 0 && cotizacion && (
          <div style={styles.estimacion}>
            Vas a recibir ≈ <strong>${dolares} USD</strong>
          </div>
        )}
        <button type="submit" disabled={loading || !montoARS} style={styles.btn}>
          {loading ? 'Procesando...' : 'Comprar dólares'}
        </button>
      </form>
    </div>
  );
}

const styles = {
  title: { fontSize: 22, fontWeight: 700, color: '#1e293b', marginBottom: 20 },
  cotizacion: {
    display: 'flex', gap: 8, alignItems: 'center', padding: '12px 16px',
    background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: 8,
    marginBottom: 20,
  },
  cotLabel: { fontSize: 13, color: '#64748b' },
  cotValor: { fontSize: 15, fontWeight: 600, color: '#1e293b' },
  success: {
    fontSize: 13, color: '#16a34a', padding: '10px 14px', background: '#f0fdf4',
    borderRadius: 6, marginBottom: 16,
  },
  error: {
    fontSize: 13, color: '#dc2626', padding: '10px 14px', background: '#fef2f2',
    borderRadius: 6, marginBottom: 16,
  },
  form: { display: 'flex', flexDirection: 'column', gap: 12, maxWidth: 360 },
  label: { fontSize: 14, fontWeight: 500, color: '#1e293b' },
  input: {
    padding: '10px 14px', border: '1px solid #e2e8f0', borderRadius: 6,
    fontSize: 14, fontFamily: "'Inter', sans-serif", outline: 'none',
  },
  estimacion: {
    padding: '10px 14px', background: '#f8fafc', borderRadius: 6,
    fontSize: 14, border: '1px solid #e2e8f0',
  },
  btn: {
    padding: '10px 20px', background: '#2563eb', color: '#fff',
    border: 'none', borderRadius: 6, cursor: 'pointer',
    fontSize: 14, fontWeight: 500, fontFamily: "'Inter', sans-serif",
  },
};
