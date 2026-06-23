package com.billeteravirtual.backend.dto.request

import jakarta.validation.constraints.NotBlank

data class LoginRequest(
    @field:NotBlank val identificador: String,
    @field:NotBlank val password: String
)
