import { useEffect, useState } from 'react';
import { api } from '../services/api';
import SaldoCard from '../components/SaldoCard';

export default function Dashboard() {
  const [cuentas, setCuentas] = useState([]);
  const [cotizacion, setCotizacion] = useState(null);
  const [error, setError] = useState('');
  const [alias, setAlias] = useState(localStorage.getItem('alias') || '');
  const [editandoAlias, setEditandoAlias] = useState(false);
  const [nuevoAlias, setNuevoAlias] = useState(alias);

  const usuarioId = Number(localStorage.getItem('usuario_id'));
  const nombre = localStorage.getItem('nombre');

  useEffect(() => {
    const load = async () => {
      try {
        const [cts, cot] = await Promise.all([
          api.getCuentas(usuarioId),
          api.getCotizacion('blue'),
        ]);
        setCuentas(cts);
        setCotizacion(cot);
      } catch (err) {
        setError(err.message);
      }
    };
    load();
  }, [usuarioId]);

  const handleGuardarAlias = async () => {
    setError('');
    try {
      const res = await api.actualizarAlias(usuarioId, nuevoAlias);
      setAlias(res.alias);
      localStorage.setItem('alias', res.alias);
      setEditandoAlias(false);
    } catch (err) {
      setError(err.message);
    }
  };

  const saldoARS = cuentas.find((c) => c.moneda === 'ARS')?.saldo ?? 0;
  const saldoUSD = cuentas.find((c) => c.moneda === 'USD')?.saldo ?? 0;

  return (
    <div>
      <div style={styles.header}>
        <div>
          <h2 style={styles.greeting}>Hola, {nombre}</h2>
          <p style={styles.aliasText}>@{alias}</p>
        </div>
        {!editandoAlias && (
          <button onClick={() => setEditandoAlias(true)} style={styles.editBtn}>Editar alias</button>
        )}
      </div>

      {error && <p style={styles.error}>{error}</p>}

      {editandoAlias && (
        <div style={styles.aliasBox}>
          <input value={nuevoAlias} onChange={(e) => setNuevoAlias(e.target.value)}
            style={styles.input} placeholder="Nuevo alias"
          />
          <div style={{ display: 'flex', gap: 8 }}>
            <button onClick={handleGuardarAlias} style={styles.btn}>Guardar</button>
            <button onClick={() => { setEditandoAlias(false); setNuevoAlias(alias); }}
              style={styles.btnSecondary}>Cancelar</button>
          </div>
        </div>
      )}

      <div style={styles.cardsRow}>
        <SaldoCard moneda="ARS" saldo={saldoARS} />
        <SaldoCard moneda="USD" saldo={saldoUSD} />
      </div>

      {cotizacion && (
        <div style={styles.cotizacionBox}>
          <h3 style={styles.sectionTitle}>Cotización Blue</h3>
          <div style={styles.cotizacionRow}>
            <div style={styles.cotItem}>
              <span style={styles.cotLabel}>Compra</span>
              <span style={styles.cotValor}>${Number(cotizacion.compra).toFixed(2)}</span>
            </div>
            <div style={styles.cotItem}>
              <span style={styles.cotLabel}>Venta</span>
              <span style={styles.cotValor}>${Number(cotizacion.venta).toFixed(2)}</span>
            </div>
          </div>
          {cotizacion.fuente && <p style={styles.cotFuente}>Fuente: {cotizacion.fuente}</p>}
        </div>
      )}
    </div>
  );
}

const styles = {
  header: { display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 24 },
  greeting: { fontSize: 24, fontWeight: 700, color: '#1e293b', margin: 0 },
  aliasText: { fontSize: 14, color: '#64748b', marginTop: 4 },
  editBtn: {
    padding: '8px 16px', fontSize: 13, fontWeight: 500, color: '#2563eb',
    background: '#eff6ff', border: 'none', borderRadius: 6, cursor: 'pointer',
  },
  error: { fontSize: 13, color: '#dc2626', padding: '8px 12px', background: '#fef2f2', borderRadius: 6, marginBottom: 16 },
  aliasBox: {
    padding: 16, border: '1px solid #e2e8f0', borderRadius: 8, marginBottom: 24,
    display: 'flex', gap: 8, alignItems: 'center',
  },
  input: {
    padding: '8px 12px', border: '1px solid #e2e8f0', borderRadius: 6,
    fontSize: 14, fontFamily: "'Inter', sans-serif", outline: 'none', flex: 1,
  },
  btn: {
    padding: '8px 16px', background: '#2563eb', color: '#fff',
    border: 'none', borderRadius: 6, cursor: 'pointer', fontSize: 13, fontWeight: 500,
  },
  btnSecondary: {
    padding: '8px 16px', background: '#fff', color: '#1e293b',
    border: '1px solid #e2e8f0', borderRadius: 6, cursor: 'pointer', fontSize: 13, fontWeight: 500,
  },
  cardsRow: { display: 'flex', gap: 16, marginBottom: 24 },
  cotizacionBox: {
    padding: 20, border: '1px solid #e2e8f0', borderRadius: 8,
  },
  sectionTitle: { fontSize: 16, fontWeight: 600, color: '#1e293b', marginBottom: 12 },
  cotizacionRow: { display: 'flex', gap: 32 },
  cotItem: { display: 'flex', flexDirection: 'column', gap: 2 },
  cotLabel: { fontSize: 12, color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.05em' },
  cotValor: { fontSize: 22, fontWeight: 700, color: '#1e293b' },
  cotFuente: { fontSize: 12, color: '#94a3b8', marginTop: 12 },
};
