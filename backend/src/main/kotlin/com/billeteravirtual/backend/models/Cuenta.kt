package com.billeteravirtual.backend.models

import jakarta.persistence.Column
import jakarta.persistence.Entity
import jakarta.persistence.EnumType
import jakarta.persistence.Enumerated
import jakarta.persistence.Id
import jakarta.persistence.JoinColumn
import jakarta.persistence.ManyToOne
import jakarta.persistence.Table
import jakarta.persistence.UniqueConstraint
import jakarta.validation.constraints.DecimalMin
import jakarta.validation.constraints.NotBlank
import jakarta.validation.constraints.NotNull
import java.math.BigDecimal
import java.util.UUID

@Entity
@Table(
    name = "cuentas",
    uniqueConstraints = [UniqueConstraint(columnNames = ["alias"])]
)
data class Cuenta(
    @Id
    @Column(name = "id", nullable = false, updatable = false, columnDefinition = "UUID")
    val id: UUID = UUID.randomUUID(),

    @ManyToOne(optional = false)
    @JoinColumn(name = "usuario_id", nullable = false)
    @NotNull
    val usuario: Usuario,

    @Enumerated(EnumType.STRING)
    @Column(name = "moneda", nullable = false, length = 3)
    @NotNull
    val moneda: Moneda,

    @Column(name = "saldo", nullable = false, precision = 19, scale = 2)
    @NotNull
    @DecimalMin(value = "0.0", inclusive = true)
    var saldo: BigDecimal = BigDecimal.ZERO,

    @Column(name = "alias", nullable = false, unique = true, length = 100)
    @NotBlank
    val alias: String
)