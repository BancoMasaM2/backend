import { useState } from 'react';
import { api } from '../services/api';
import FormTransferencia from '../components/FormTransferencia';

export default function Transferencias() {
  const [step, setStep] = useState('form');
  const [mensaje, setMensaje] = useState('');
  const [error, setError] = useState('');
  const [codigo, setCodigo] = useState('');
  const [loading, setLoading] = useState(false);
  const usuarioId = Number(localStorage.getItem('usuario_id'));

  const handleInit = async ({ destinoAlias, moneda, monto }) => {
    setMensaje('');
    setError('');
    setLoading(true);
    try {
      await api.iniciarTransferencia(usuarioId, destinoAlias, moneda, monto);
      setMensaje('Código de confirmación enviado a tu email');
      setStep('verificar');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleConfirm = async (e) => {
    e.preventDefault();
    setMensaje('');
    setError('');
    setLoading(true);
    try {
      const res = await api.confirmarTransferencia(usuarioId, codigo);
      setMensaje(`Transferencia exitosa. ID: ${res.detalle.transferencia_id}`);
      setStep('form');
      setCodigo('');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (step === 'verificar') {
    return (
      <div>
        <h2 style={styles.title}>Confirmar transferencia</h2>
        {mensaje && <p style={styles.success}>{mensaje}</p>}
        {error && <p style={styles.error}>{error}</p>}
        <form onSubmit={handleConfirm} style={styles.form}>
          <input placeholder="Código de verificación" value={codigo}
            onChange={(e) => setCodigo(e.target.value)}
            style={styles.input} maxLength={6} required
          />
          <button type="submit" disabled={loading} style={styles.btn}>
            {loading ? 'Verificando...' : 'Confirmar transferencia'}
          </button>
          <button type="button" onClick={() => { setStep('form'); setError(''); setMensaje(''); }}
            style={styles.btnSecondary}>Cancelar</button>
        </form>
      </div>
    );
  }

  return (
    <div>
      <h2 style={styles.title}>Transferencias</h2>
      {mensaje && <p style={styles.success}>{mensaje}</p>}
      {error && <p style={styles.error}>{error}</p>}
      <FormTransferencia onSubmit={handleInit} loading={loading} />
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
  btnSecondary: {
    padding: '10px 20px', background: '#fff', color: '#1e293b',
    border: '1px solid #e2e8f0', borderRadius: 6, cursor: 'pointer',
    fontSize: 14, fontWeight: 500, fontFamily: "'Inter', sans-serif",
  },
};
