package com.billeteravirtual.backend.dto.request

import jakarta.validation.constraints.Email
import jakarta.validation.constraints.NotBlank

data class OlvidePasswordRequest(
    @field:NotBlank @field:Email val email: String
)
