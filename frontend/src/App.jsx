import { Routes, Route, Navigate, useLocation } from 'react-router-dom';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import Login from './pages/Login';
import Registro from './pages/Registro';
import Dashboard from './pages/Dashboard';
import Transferencias from './pages/Transferencias';
import ComprarDolares from './pages/ComprarDolares';
import Pagos from './pages/Pagos';
import Historial from './pages/Historial';

function isAuthenticated() {
  return !!localStorage.getItem('usuario_id');
}

function ProtectedRoute({ children }) {
  return isAuthenticated() ? children : <Navigate to="/login" />;
}

export default function App() {
  const location = useLocation();
  const isHome = location.pathname === '/';

  return (
    <>
      {isAuthenticated() && !isHome && <Navbar />}
      {isHome ? (
        <Home />
      ) : (
        <div style={{ padding: '24px', maxWidth: 960, margin: '0 auto' }}>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/registro" element={<Registro />} />
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <Dashboard />
                </ProtectedRoute>
              }
            />
            <Route
            path="/transferencias"
            element={
              <ProtectedRoute>
                <Transferencias />
              </ProtectedRoute>
            }
          />
          <Route
            path="/comprar-dolares"
            element={
              <ProtectedRoute>
                <ComprarDolares />
              </ProtectedRoute>
            }
          />
          <Route
            path="/pagos"
              element={
                <ProtectedRoute>
                  <Pagos />
                </ProtectedRoute>
              }
            />
            <Route
              path="/historial"
              element={
                <ProtectedRoute>
                  <Historial />
                </ProtectedRoute>
              }
            />
            <Route path="*" element={<Navigate to="/" />} />
          </Routes>
        </div>
      )}
    </>
  );
}
