package com.billeteravirtual.backend.dto.request

import jakarta.validation.constraints.NotBlank
import jakarta.validation.constraints.Size
import java.util.UUID

data class ConfirmarTransferenciaRequest(
    @field:NotBlank val idTransaccion: UUID,
    @field:NotBlank @field:Size(min = 6, max = 6) val codigoAutorizacion: String
)
