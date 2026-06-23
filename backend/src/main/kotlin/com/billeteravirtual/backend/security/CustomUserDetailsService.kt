package com.billeteravirtual.backend.security

import com.billeteravirtual.backend.repository.UsuarioRepository
import org.springframework.security.core.userdetails.User
import org.springframework.security.core.userdetails.UserDetails
import org.springframework.security.core.userdetails.UserDetailsService
import org.springframework.security.core.userdetails.UsernameNotFoundException
import org.springframework.stereotype.Service

@Service
class CustomUserDetailsService(
    private val usuarioRepository: UsuarioRepository
) : UserDetailsService {

    override fun loadUserByUsername(email: String): UserDetails {
        val usuario = usuarioRepository.findByEmail(email)
            .orElseThrow { UsernameNotFoundException("Usuario no encontrado: $email") }
        return User.builder()
            .username(usuario.email)
            .password(usuario.passwordHash)
            .authorities(emptyList())
            .build()
    }
}
