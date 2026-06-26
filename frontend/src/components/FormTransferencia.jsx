import { useState } from 'react';

export default function FormTransferencia({ onSubmit, loading }) {
  const [form, setForm] = useState({
    destinoAlias: '',
    moneda: 'ARS',
    monto: '',
  });

  const handleChange = (e) =>
    setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit({
      destinoAlias: form.destinoAlias,
      moneda: form.moneda,
      monto: Number(form.monto),
    });
  };

  return (
    <form onSubmit={handleSubmit} style={styles.form}>
      <h3 style={styles.heading}>Nueva transferencia</h3>
      <input
        name="destinoAlias" placeholder="Alias del destinatario"
        value={form.destinoAlias} onChange={handleChange}
        style={styles.input} required
      />
      <select name="moneda" value={form.moneda} onChange={handleChange} style={styles.input}>
        <option value="ARS">ARS</option>
        <option value="USD">USD</option>
      </select>
      <input
        name="monto" type="number" step="0.01" min="0.01" placeholder="Monto"
        value={form.monto} onChange={handleChange}
        style={styles.input} required
      />
      <button type="submit" disabled={loading} style={styles.btn}>
        {loading ? 'Enviando...' : 'Transferir'}
      </button>
    </form>
  );
}

const styles = {
  form: { display: 'flex', flexDirection: 'column', gap: 12, maxWidth: 360 },
  heading: { fontSize: 16, fontWeight: 600, color: '#1e293b', margin: '0 0 4px' },
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
