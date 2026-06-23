package com.billeteravirtual.backend.dto.request

import jakarta.validation.constraints.Email
import jakarta.validation.constraints.NotBlank
import jakarta.validation.constraints.Size

data class ValidarEmailRequest(
    @field:NotBlank @field:Email val email: String,
    @field:NotBlank @field:Size(min = 6, max = 6) val codigo: String
)
