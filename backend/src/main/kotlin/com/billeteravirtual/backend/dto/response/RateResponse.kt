package com.billeteravirtual.backend.dto.response

import java.math.BigDecimal
import java.time.LocalDateTime

data class RateResponse(
    val monedaBase: String,
    val monedaDestino: String,
    val cotizacionOficial: BigDecimal,
    val fechaActualizacion: LocalDateTime
)
