package com.billeteravirtual.backend.dto.request

import jakarta.validation.constraints.Email
import jakarta.validation.constraints.NotBlank
import jakarta.validation.constraints.Past
import jakarta.validation.constraints.Size
import java.time.LocalDate

data class RegistroRequest(
    @field:NotBlank @field:Email val email: String,
    @field:NotBlank @field:Size(min = 8) val password: String,
    @field:NotBlank val nombreCompleto: String,
    @field:NotBlank val dni: String,
    @field:Past val fechaNacimiento: LocalDate
)
