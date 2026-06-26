import { Link, useNavigate, useLocation } from 'react-router-dom';

export default function Navbar() {
  const navigate = useNavigate();
  const location = useLocation();
  const alias = localStorage.getItem('alias');
  const nombre = localStorage.getItem('nombre');

  const handleLogout = () => {
    localStorage.removeItem('usuario_id');
    localStorage.removeItem('nombre');
    localStorage.removeItem('alias');
    navigate('/login');
  };

  const links = [
    { to: '/dashboard', label: 'Dashboard' },
    { to: '/transferencias', label: 'Transferencias' },
    { to: '/comprar-dolares', label: 'Comprar Dólares' },
    { to: '/pagos', label: 'Pagos' },
    { to: '/historial', label: 'Historial' },
  ];

  return (
    <nav style={styles.nav}>
      <div style={styles.left}>
        <Link to="/dashboard" style={styles.brand}>Banco GCDR</Link>
        <div style={styles.links}>
          {links.map((l) => (
            <Link
              key={l.to}
              to={l.to}
              style={{
                ...styles.link,
                ...(location.pathname === l.to ? styles.linkActive : {}),
              }}
            >
              {l.label}
            </Link>
          ))}
        </div>
      </div>
      <div style={styles.right}>
        <span style={styles.userInfo}>{nombre}</span>
        <button onClick={handleLogout} style={styles.logoutBtn}>Salir</button>
      </div>
    </nav>
  );
}

const styles = {
  nav: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    height: 56,
    padding: '0 24px',
    borderBottom: '1px solid #e2e8f0',
    background: '#fff',
  },
  left: { display: 'flex', alignItems: 'center', gap: 32 },
  brand: { fontSize: 16, fontWeight: 700, color: '#1e293b', textDecoration: 'none' },
  links: { display: 'flex', gap: 4 },
  link: {
    padding: '8px 14px',
    fontSize: 13,
    fontWeight: 500,
    color: '#64748b',
    textDecoration: 'none',
    borderRadius: 6,
    transition: 'background 0.15s, color 0.15s',
  },
  linkActive: {
    background: '#f1f5f9',
    color: '#2563eb',
  },
  right: { display: 'flex', alignItems: 'center', gap: 16 },
  userInfo: { fontSize: 13, color: '#64748b', fontWeight: 500 },
  logoutBtn: {
    padding: '6px 14px',
    fontSize: 13,
    fontWeight: 500,
    color: '#64748b',
    background: '#f1f5f9',
    border: 'none',
    borderRadius: 6,
    cursor: 'pointer',
  },
};
