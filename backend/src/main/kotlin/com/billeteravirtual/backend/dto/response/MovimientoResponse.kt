package com.billeteravirtual.backend.dto.response

import java.math.BigDecimal
import java.time.LocalDateTime
import java.util.UUID

data class MovimientoResponse(
    val id: UUID,
    val cuentaOrigenAlias: String?,
    val cuentaDestinoAlias: String?,
    val monto: BigDecimal,
    val moneda: String,
    val tipo: String,
    val estado: String,
    val fechaCreacion: LocalDateTime,
    val descripcion: String?
)
