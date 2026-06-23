package com.billeteravirtual.backend.repository

import com.billeteravirtual.backend.models.Cuenta
import com.billeteravirtual.backend.models.Movimiento
import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.stereotype.Repository
import java.util.Optional
import java.util.UUID

@Repository
interface MovimientoRepository : JpaRepository<Movimiento, UUID> {
    fun findByCuentaOrigenOrCuentaDestinoOrderByFechaCreacionDesc(
        cuentaOrigen: Cuenta,
        cuentaDestino: Cuenta
    ): List<Movimiento>

    fun findByCuentaOrigenAndCodigoAutorizacion(
        cuentaOrigen: Cuenta,
        codigoAutorizacion: String
    ): Optional<Movimiento>
}
