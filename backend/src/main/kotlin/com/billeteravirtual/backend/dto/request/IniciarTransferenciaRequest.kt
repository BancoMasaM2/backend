package com.billeteravirtual.backend.dto.request

import jakarta.validation.constraints.DecimalMin
import jakarta.validation.constraints.NotBlank
import jakarta.validation.constraints.NotNull
import java.math.BigDecimal

data class IniciarTransferenciaRequest(
    @field:NotBlank val cuentaOrigen: String,
    @field:NotBlank val aliasDestino: String,
    @field:NotNull @field:DecimalMin(value = "0.01") val monto: BigDecimal
)
