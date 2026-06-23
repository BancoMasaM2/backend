package com.billeteravirtual.backend.service

import com.billeteravirtual.backend.dto.response.UsuarioResponse
import com.billeteravirtual.backend.repository.UsuarioRepository
import org.springframework.stereotype.Service

@Service
class UsuarioService(
    private val usuarioRepository: UsuarioRepository
) {
    fun obtenerUsuario(email: String): UsuarioResponse? {
        val usuario = usuarioRepository.findByEmail(email).orElse(null) ?: return null
        return UsuarioResponse(
            email = usuario.email,
            nombreCompleto = usuario.nombreCompleto
        )
    }
}
