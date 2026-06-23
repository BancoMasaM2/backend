package com.billeteravirtual.backend.dto.request

import jakarta.validation.constraints.NotBlank
import jakarta.validation.constraints.Size

data class ResetPasswordRequest(
    @field:NotBlank val tokenUrl: String,
    @field:NotBlank @field:Size(min = 8) val nuevaPassword: String,
    @field:NotBlank @field:Size(min = 8) val confirmarPassword: String
)
