export default function SaldoCard({ moneda, saldo }) {
  const saldoStr = saldo !== undefined && saldo !== null
    ? Number(saldo).toLocaleString('es-AR', { minimumFractionDigits: 2 })
    : '---';

  return (
    <div style={styles.card}>
      <div style={styles.header}>
        <span style={styles.moneda}>{moneda}</span>
      </div>
      <div style={styles.saldo}>
        {moneda === 'USD' ? 'U$S' : '$'} {saldoStr}
      </div>
    </div>
  );
}

const styles = {
  card: {
    border: '1px solid #e2e8f0',
    borderRadius: 8,
    padding: 20,
    minWidth: 180,
    flex: 1,
    background: '#fff',
  },
  header: { marginBottom: 8 },
  moneda: {
    fontSize: 12, fontWeight: 600, color: '#64748b',
    textTransform: 'uppercase', letterSpacing: '0.05em',
  },
  saldo: { fontSize: 26, fontWeight: 700, color: '#1e293b' },
};
