package com.billeteravirtual.backend.service

import com.billeteravirtual.backend.dto.request.LoginRequest
import com.billeteravirtual.backend.dto.request.OlvidePasswordRequest
import com.billeteravirtual.backend.dto.request.RegistroRequest
import com.billeteravirtual.backend.dto.request.ResetPasswordRequest
import com.billeteravirtual.backend.dto.request.ValidarEmailRequest
import com.billeteravirtual.backend.dto.response.AuthResponse
import com.billeteravirtual.backend.models.Cuenta
import com.billeteravirtual.backend.models.EstadoEmail
import com.billeteravirtual.backend.models.Moneda
import com.billeteravirtual.backend.models.Usuario
import com.billeteravirtual.backend.repository.CuentaRepository
import com.billeteravirtual.backend.repository.UsuarioRepository
import org.springframework.security.authentication.AuthenticationManager
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken
import org.springframework.security.crypto.password.PasswordEncoder
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import java.util.UUID

@Service
class AuthService(
    private val usuarioRepository: UsuarioRepository,
    private val cuentaRepository: CuentaRepository,
    private val passwordEncoder: PasswordEncoder,
    private val authenticationManager: AuthenticationManager
) {
    @Transactional
    fun registrar(request: RegistroRequest): AuthResponse {
        if (usuarioRepository.existsByEmail(request.email)) {
            return AuthResponse(mensaje = "El email ya está registrado", success = false)
        }
        if (usuarioRepository.existsByDni(request.dni)) {
            return AuthResponse(mensaje = "El DNI ya está registrado", success = false)
        }
        val codigo = generarCodigoVerificacion()
        val usuario = Usuario(
            dni = request.dni,
            email = request.email,
            passwordHash = passwordEncoder.encode(request.password),
            nombreCompleto = request.nombreCompleto,
            fechaNacimiento = request.fechaNacimiento,
            codigoVerificacionEmail = codigo
        )
        usuarioRepository.save(usuario)

        val aliasArs = "${usuario.nombreCompleto.lowercase().replace(" ", ".")}.ars"
        val aliasUsd = "${usuario.nombreCompleto.lowercase().replace(" ", ".")}.usd"

        cuentaRepository.save(Cuenta(usuario = usuario, moneda = Moneda.ARS, alias = aliasArs))
        cuentaRepository.save(Cuenta(usuario = usuario, moneda = Moneda.USD, alias = aliasUsd))

        return AuthResponse(mensaje = "Registro exitoso. Revisa tu correo para verificar tu email.", success = true)
    }

    fun validarEmail(request: ValidarEmailRequest): AuthResponse {
        val usuario = usuarioRepository.findByEmail(request.email)
            .orElse(null) ?: return AuthResponse(mensaje = "Usuario no encontrado", success = false)

        if (usuario.estadoEmail == EstadoEmail.VERIFICADO) {
            return AuthResponse(mensaje = "El email ya está verificado", success = true)
        }
        if (usuario.codigoVerificacionEmail != request.codigo) {
            return AuthResponse(mensaje = "Código inválido", success = false)
        }
        usuarioRepository.save(usuario.copy(estadoEmail = EstadoEmail.VERIFICADO, codigoVerificacionEmail = null))
        return AuthResponse(mensaje = "Email verificado exitosamente", success = true)
    }

    fun login(request: LoginRequest): AuthResponse {
        val usuario = usuarioRepository.findByEmail(request.identificador)
            .orElseGet {
                usuarioRepository.findByDni(request.identificador).orElse(null)
            } ?: return AuthResponse(mensaje = "Credenciales inválidas", success = false)

        authenticationManager.authenticate(
            UsernamePasswordAuthenticationToken(usuario.email, request.password)
        )
        return AuthResponse(mensaje = "Inicio de sesión exitoso", success = true)
    }

    fun olvidePassword(request: OlvidePasswordRequest): AuthResponse {
        val usuario = usuarioRepository.findByEmail(request.email)
            .orElse(null) ?: return AuthResponse(mensaje = "Si el email existe, recibirás un link", success = true)

        val token = UUID.randomUUID().toString()
        usuarioRepository.save(usuario.copy(tokenRecuperacionPass = token))
        return AuthResponse(mensaje = "Revisa tu correo para restablecer tu contraseña", success = true)
    }

    @Transactional
    fun resetPassword(request: ResetPasswordRequest): AuthResponse {
        if (request.nuevaPassword != request.confirmarPassword) {
            return AuthResponse(mensaje = "Las contraseñas no coinciden", success = false)
        }
        val usuario = usuarioRepository.findAll().find { it.tokenRecuperacionPass == request.tokenUrl }
            ?: return AuthResponse(mensaje = "Token inválido o expirado", success = false)

        usuarioRepository.save(
            usuario.copy(
                passwordHash = passwordEncoder.encode(request.nuevaPassword),
                tokenRecuperacionPass = null
            )
        )
        return AuthResponse(mensaje = "Contraseña actualizada exitosamente", success = true)
    }

    private fun generarCodigoVerificacion(): String {
        val nums = (1..6).map { (0..9).random() }
        return nums.joinToString("")
    }
}
