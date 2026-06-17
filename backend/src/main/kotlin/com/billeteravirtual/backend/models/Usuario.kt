package com.billeteravirtual.backend.models

import jakarta.persistence.Column
import jakarta.persistence.Entity
import jakarta.persistence.EnumType
import jakarta.persistence.Enumerated
import jakarta.persistence.Id
import jakarta.persistence.Table
import jakarta.validation.constraints.Email
import jakarta.validation.constraints.NotBlank
import jakarta.validation.constraints.NotNull
import java.time.LocalDate
import java.util.UUID

@Entity
@Table(name = "usuarios")
data class Usuario(
    @Id
    @Column(name = "id", nullable = false, updatable = false, columnDefinition = "UUID")
    val id: UUID = UUID.randomUUID(),

    @Column(name = "dni", nullable = false, unique = true, length = 20)
    @NotBlank
    val dni: String,

    @Column(name = "email", nullable = false, unique = true, length = 255)
    @NotBlank
    @Email
    val email: String,

    @Column(name = "password_hash", nullable = false)
    @NotBlank
    val passwordHash: String,

    @Column(name = "nombre_completo", nullable = false, length = 255)
    @NotBlank
    val nombreCompleto: String,

    @Column(name = "fecha_nacimiento", nullable = false)
    @NotNull
    val fechaNacimiento: LocalDate,

    @Enumerated(EnumType.STRING)
    @Column(name = "estado_email", nullable = false, length = 20)
    @NotNull
    val estadoEmail: EstadoEmail = EstadoEmail.PENDIENTE,

    @Column(name = "codigo_verificacion_email", length = 6)
    var codigoVerificacionEmail: String? = null,

    @Column(name = "token_recuperacion_pass", length = 255)
    var tokenRecuperacionPass: String? = null
)