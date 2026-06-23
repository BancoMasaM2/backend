package com.billeteravirtual.backend.repository

import com.billeteravirtual.backend.models.Usuario
import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.stereotype.Repository
import java.util.Optional
import java.util.UUID

@Repository
interface UsuarioRepository : JpaRepository<Usuario, UUID> {
    fun findByEmail(email: String): Optional<Usuario>
    fun findByDni(dni: String): Optional<Usuario>
    fun existsByEmail(email: String): Boolean
    fun existsByDni(dni: String): Boolean
}
