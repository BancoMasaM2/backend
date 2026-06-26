import { useEffect, useState } from 'react';
import { api } from '../services/api';

export default function Historial() {
  const [movimientos, setMovimientos] = useState([]);
  const [error, setError] = useState('');

  const usuarioId = Number(localStorage.getItem('usuario_id'));

  useEffect(() => {
    const load = async () => {
      try {
        const data = await api.getMovimientos(usuarioId);
        setMovimientos(data);
      } catch (err) {
        setError(err.message);
      }
    };
    load();
  }, [usuarioId]);

  return (
    <div>
      <h2 style={styles.title}>Historial</h2>
      {error && <p style={styles.error}>{error}</p>}
      {movimientos.length === 0 ? (
        <p style={styles.empty}>No hay movimientos registrados.</p>
      ) : (
        <div style={styles.tableWrap}>
          <table style={styles.table}>
            <thead>
              <tr>
                <th style={styles.th}>Fecha</th>
                <th style={styles.th}>Concepto</th>
                <th style={styles.th}>Monto</th>
                <th style={styles.th}>Estado</th>
              </tr>
            </thead>
            <tbody>
              {movimientos.map((m) => (
                <tr key={m.id} style={styles.tr}>
                  <td style={styles.td}>{m.fecha ? new Date(m.fecha).toLocaleString() : '-'}</td>
                  <td style={styles.td}>{m.concepto}</td>
                  <td style={{
                    ...styles.td,
                    color: m.es_ingreso ? '#16a34a' : '#dc2626',
                    fontWeight: 500,
                  }}>
                    {m.es_ingreso ? '+' : '-'}${Number(m.monto).toFixed(2)} {m.moneda}
                  </td>
                  <td style={styles.td}>
                    <span style={m.estado === 'completada' ? styles.badgeSuccess : styles.badge}>
                      {m.estado}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

const styles = {
  title: { fontSize: 22, fontWeight: 700, color: '#1e293b', marginBottom: 20 },
  error: {
    fontSize: 13, color: '#dc2626', padding: '8px 12px', background: '#fef2f2',
    borderRadius: 6, marginBottom: 16,
  },
  empty: { fontSize: 14, color: '#94a3b8' },
  tableWrap: { border: '1px solid #e2e8f0', borderRadius: 8, overflow: 'hidden' },
  table: { width: '100%', borderCollapse: 'collapse', fontSize: 14 },
  th: {
    textAlign: 'left', padding: '12px 16px', fontSize: 12,
    color: '#64748b', fontWeight: 600, textTransform: 'uppercase',
    letterSpacing: '0.05em', background: '#f8fafc',
    borderBottom: '1px solid #e2e8f0',
  },
  tr: { borderBottom: '1px solid #f1f5f9' },
  td: { padding: '12px 16px', color: '#1e293b' },
  badge: {
    fontSize: 12, padding: '2px 8px', borderRadius: 4,
    background: '#f1f5f9', color: '#64748b',
  },
  badgeSuccess: {
    fontSize: 12, padding: '2px 8px', borderRadius: 4,
    background: '#f0fdf4', color: '#16a34a',
  },
};
