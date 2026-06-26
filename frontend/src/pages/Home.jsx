import { Link } from 'react-router-dom';

export default function Home() {
  return (
    <div>
      <header style={styles.header}>
        <Link to="/" style={styles.logo}>Banco GCDR</Link>
        <div style={styles.headerRight}>
          <Link to="/login" style={styles.loginLink}>Ingresar</Link>
          <Link to="/registro" style={styles.registerLink}>Abrir cuenta</Link>
        </div>
      </header>

      <section style={styles.hero}>
        <h1 style={styles.heroTitle}>Tu banco 100% digital</h1>
        <p style={styles.heroSub}>Administrá tu plata en ARS y USD, convertí al instante, transferí sin demoras. Simple, rápido y seguro.</p>
        <div style={styles.heroActions}>
          <Link to="/registro" style={styles.btnPrimary}>Crear cuenta gratis</Link>
          <Link to="/login" style={styles.btnSecondary}>Ingresar a GCDR Online</Link>
        </div>
      </section>

      <section style={styles.features}>
        <div style={styles.featureGrid}>
          <div style={styles.featureCard}>
            <h3 style={styles.featureTitle}>Cuentas ARS y USD</h3>
            <p style={styles.featureDesc}>Administrá pesos y dólares desde una misma plataforma, sin costos de mantenimiento.</p>
          </div>
          <div style={styles.featureCard}>
            <h3 style={styles.featureTitle}>Conversión al instante</h3>
            <p style={styles.featureDesc}>Compra y vendé dólar blue al tipo de cambio real. Sin demoras ni comisiones ocultas.</p>
          </div>
          <div style={styles.featureCard}>
            <h3 style={styles.featureTitle}>Transferencias inmediatas</h3>
            <p style={styles.featureDesc}>Envía y recibí dinero al instante entre usuarios de Banco GCDR.</p>
          </div>
          <div style={styles.featureCard}>
            <h3 style={styles.featureTitle}>Seguridad garantizada</h3>
            <p style={styles.featureDesc}>Autenticación de dos factores y cifrado de última generación para proteger tus datos.</p>
          </div>
          <div style={styles.featureCard}>
            <h3 style={styles.featureTitle}>100% digital</h3>
            <p style={styles.featureDesc}>Operá desde cualquier dispositivo, las 24 horas. Sin sucursales ni filas.</p>
          </div>
          <div style={styles.featureCard}>
            <h3 style={styles.featureTitle}>Pagos en línea</h3>
            <p style={styles.featureDesc}>Realizá pagos desde tu cuenta ARS de forma rápida y sencilla.</p>
          </div>
        </div>
      </section>

      <section style={styles.ctaBanner}>
        <h2 style={styles.ctaTitle}>Sumate a Banco GCDR</h2>
        <p style={styles.ctaDesc}>Abrí tu cuenta en menos de 2 minutos. Sin papeles, sin trámites.</p>
        <Link to="/registro" style={styles.btnPrimary}>Crear cuenta gratis</Link>
      </section>

      <footer style={styles.footer}>
        <p>Banco GCDR &mdash; banco.gcdr@gmail.com</p>
      </footer>
    </div>
  );
}

const styles = {
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    height: 64,
    padding: '0 32px',
    maxWidth: 1100,
    margin: '0 auto',
  },
  logo: { fontSize: 20, fontWeight: 700, color: '#1e293b', textDecoration: 'none' },
  headerRight: { display: 'flex', gap: 12, alignItems: 'center' },
  loginLink: {
    color: '#64748b',
    fontSize: 14,
    fontWeight: 500,
    textDecoration: 'none',
    padding: '8px 16px',
  },
  registerLink: {
    background: '#2563eb',
    color: '#fff',
    fontSize: 14,
    fontWeight: 500,
    textDecoration: 'none',
    padding: '8px 20px',
    borderRadius: 6,
  },
  hero: {
    textAlign: 'center',
    padding: '120px 24px 100px',
    maxWidth: 700,
    margin: '0 auto',
  },
  heroTitle: { fontSize: 40, fontWeight: 700, color: '#1e293b', marginBottom: 16, lineHeight: 1.2 },
  heroSub: { fontSize: 17, color: '#64748b', lineHeight: 1.7, marginBottom: 36 },
  heroActions: { display: 'flex', gap: 12, justifyContent: 'center' },
  btnPrimary: {
    background: '#2563eb', color: '#fff', padding: '12px 28px', borderRadius: 6,
    textDecoration: 'none', fontWeight: 500, fontSize: 15, display: 'inline-block',
  },
  btnSecondary: {
    background: '#fff', color: '#2563eb', padding: '12px 28px', borderRadius: 6,
    textDecoration: 'none', fontWeight: 500, fontSize: 15, display: 'inline-block',
    border: '1px solid #2563eb',
  },
  features: { maxWidth: 1100, margin: '0 auto', padding: '0 24px 80px' },
  featureGrid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: 16 },
  featureCard: {
    padding: 24,
    borderRadius: 8,
    border: '1px solid #e2e8f0',
    background: '#fff',
  },
  featureTitle: { fontSize: 16, fontWeight: 600, color: '#1e293b', marginBottom: 8 },
  featureDesc: { fontSize: 14, color: '#64748b', lineHeight: 1.6 },
  ctaBanner: {
    textAlign: 'center', padding: '80px 24px',
    background: '#f8fafc', borderTop: '1px solid #e2e8f0',
  },
  ctaTitle: { fontSize: 28, fontWeight: 700, color: '#1e293b', marginBottom: 12 },
  ctaDesc: { fontSize: 15, color: '#64748b', marginBottom: 28 },
  footer: {
    textAlign: 'center', padding: '24px', fontSize: 13, color: '#94a3b8',
  },
};
