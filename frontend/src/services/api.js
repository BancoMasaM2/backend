const GATEWAY_URL = import.meta.env.VITE_GATEWAY_URL || 'http://localhost:7000';  //apuntar al proxy

async function request(method, path, body = null, params = {}) {
  const headers = { 'Content-Type': 'application/json' };
  const query = new URLSearchParams(params).toString();
  const url = query ? `${GATEWAY_URL}${path}?${query}` : `${GATEWAY_URL}${path}`;

  const res = await fetch(url, {
    method,
    headers,
    body: body ? JSON.stringify(body) : null,
  });

  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.detail || 'Error en la solicitud');
  }
  return data;
}

export const api = {
  login: (email, password) =>
    request('POST', '/api/auth/login', { email, password }),

  registro: (nombre, email, password) =>
    request('POST', '/api/auth/registro', { nombre, email, password }),

  verificarCodigo: (email, codigo) =>
    request('POST', '/api/auth/verificar-codigo', { email, codigo }),

  reenviarCodigo: (email) =>
    request('POST', '/api/auth/reenviar-codigo', { email }),

  getPerfil: (usuarioId) =>
    request('GET', `/api/usuarios/${usuarioId}`),

  getCuentas: (usuarioId) =>
    request('GET', `/api/cuentas/${usuarioId}`),

  transferir: (origenUsuarioId, destinoUsuarioId, moneda, monto) =>
    request('POST', '/payments/transferencias', {
      origen_usuario_id: origenUsuarioId,
      destino_usuario_id: destinoUsuarioId,
      moneda,
      monto,
    }),

  iniciarTransferencia: (origenUsuarioId, destinoAlias, moneda, monto) =>
    request('POST', '/api/operaciones/iniciar-transferencia', {
      origen_usuario_id: origenUsuarioId,
      destino_alias: destinoAlias,
      moneda,
      monto,
    }),

  confirmarTransferencia: (origenUsuarioId, codigo) =>
    request('POST', '/api/operaciones/confirmar-transferencia', {
      origen_usuario_id: origenUsuarioId,
      codigo,
    }),

  actualizarAlias: (usuarioId, alias) =>
    request('PUT', `/api/usuarios/${usuarioId}/alias`, { alias }),

  getMovimientos: (usuarioId) =>
    request('GET', `/api/usuarios/${usuarioId}/movimientos`),

  getUsuarioPorAlias: (alias) =>
    request('GET', `/api/usuarios/alias/${alias}`),

  convertir: (usuarioId, monto, desde, hacia) =>
    request('POST', '/payments/conversiones', {
      usuario_id: usuarioId,
      monto,
      desde,
      hacia,
    }),

  pagar: (usuarioId, monto, descripcion) =>
    request('POST', '/payments/pagos', {
      usuario_id: usuarioId,
      monto,
      descripcion,
    }),

  getCotizacion: (tipo = 'blue') =>
    request('GET', '/payments/cotizacion', null, { tipo }),
};
