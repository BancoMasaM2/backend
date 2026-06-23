package com.billeteravirtual.backend.service

import com.billeteravirtual.backend.dto.response.CuentaResponse
import com.billeteravirtual.backend.dto.response.MovimientoResponse
import com.billeteravirtual.backend.dto.response.WalletResponse
import com.billeteravirtual.backend.models.Cuenta
import com.billeteravirtual.backend.models.Usuario
import com.billeteravirtual.backend.repository.CuentaRepository
import com.billeteravirtual.backend.repository.MovimientoRepository
import com.billeteravirtual.backend.repository.UsuarioRepository
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional

@Service
class WalletService(
    private val usuarioRepository: UsuarioRepository,
    private val cuentaRepository: CuentaRepository,
    private val movimientoRepository: MovimientoRepository
) {
    @Transactional(readOnly = true)
    fun obtenerEstado(email: String): WalletResponse? {
        val usuario = usuarioRepository.findByEmail(email).orElse(null) ?: return null
        val cuentas = cuentaRepository.findByUsuario(usuario)
        return WalletResponse(
            usuario = usuario.nombreCompleto,
            cuentas = cuentas.map {
                CuentaResponse(
                    moneda = it.moneda.name,
                    saldo = it.saldo,
                    alias = it.alias
                )
            }
        )
    }

    @Transactional(readOnly = true)
    fun obtenerMovimientos(email: String): List<MovimientoResponse> {
        val usuario = usuarioRepository.findByEmail(email).orElse(null) ?: return emptyList()
        val cuentas = cuentaRepository.findByUsuario(usuario)
        val movimientos = cuentas.flatMap { cuenta ->
            movimientoRepository.findByCuentaOrigenOrCuentaDestinoOrderByFechaCreacionDesc(cuenta, cuenta)
        }.distinct().sortedByDescending { it.fechaCreacion }
        return movimientos.map {
            MovimientoResponse(
                id = it.id,
                cuentaOrigenAlias = it.cuentaOrigen?.alias,
                cuentaDestinoAlias = it.cuentaDestino.alias,
                monto = it.monto,
                moneda = it.cuentaDestino.moneda.name,
                tipo = it.tipoMovimiento.name,
                estado = it.estadoMovimiento.name,
                fechaCreacion = it.fechaCreacion,
                descripcion = it.descripcion
            )
        }
    }
}
