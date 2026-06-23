package com.billeteravirtual.backend.models

import jakarta.persistence.Column
import jakarta.persistence.Entity
import jakarta.persistence.EnumType
import jakarta.persistence.Enumerated
import jakarta.persistence.Id
import jakarta.persistence.JoinColumn
import jakarta.persistence.ManyToOne
import jakarta.persistence.Table
import jakarta.validation.constraints.DecimalMin
import jakarta.validation.constraints.NotNull
import java.math.BigDecimal
import java.time.LocalDateTime
import java.util.UUID

@Entity
@Table(name = "movimientos")
data class Movimiento(
    @Id
    @Column(name = "id", nullable = false, updatable = false, columnDefinition = "UUID")
    val id: UUID = UUID.randomUUID(),

    @ManyToOne(optional = true)
    @JoinColumn(name = "cuenta_origen_id", nullable = true)
    val cuentaOrigen: Cuenta?,

    @ManyToOne(optional = false)
    @JoinColumn(name = "cuenta_destino_id", nullable = false)
    @NotNull
    val cuentaDestino: Cuenta,

    @Column(name = "monto", nullable = false, precision = 19, scale = 2)
    @NotNull
    @DecimalMin(value = "0.01", inclusive = true)
    val monto: BigDecimal,

    @Enumerated(EnumType.STRING)
    @Column(name = "tipo_movimiento", nullable = false, length = 20)
    @NotNull
    val tipoMovimiento: TipoMovimiento,

    @Enumerated(EnumType.STRING)
    @Column(name = "estado_movimiento", nullable = false, length = 20)
    @NotNull
    var estadoMovimiento: EstadoMovimiento = EstadoMovimiento.PENDIENTE_AUTORIZACION,

    @Column(name = "descripcion", length = 500)
    val descripcion: String? = null,

    @Column(name = "fecha_creacion", nullable = false, updatable = false)
    @NotNull
    val fechaCreacion: LocalDateTime = LocalDateTime.now(),

    @Column(name = "fecha_autorizacion")
    val fechaAutorizacion: LocalDateTime? = null,

    @Column(name = "codigo_autorizacion", length = 6)
    var codigoAutorizacion: String? = null
)