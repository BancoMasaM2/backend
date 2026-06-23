package com.billeteravirtual.backend.repository

import com.billeteravirtual.backend.models.Cuenta
import com.billeteravirtual.backend.models.Moneda
import com.billeteravirtual.backend.models.Usuario
import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.stereotype.Repository
import java.util.Optional
import java.util.UUID

@Repository
interface CuentaRepository : JpaRepository<Cuenta, UUID> {
    fun findByUsuario(usuario: Usuario): List<Cuenta>
    fun findByUsuarioAndMoneda(usuario: Usuario, moneda: Moneda): Optional<Cuenta>
    fun findByAlias(alias: String): Optional<Cuenta>
    fun existsByAlias(alias: String): Boolean
}
