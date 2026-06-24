package com.billeteravirtual.backend.controller

import com.billeteravirtual.backend.dto.request.LoginRequest
import com.billeteravirtual.backend.dto.request.OlvidePasswordRequest
import com.billeteravirtual.backend.dto.request.RegistroRequest
import com.billeteravirtual.backend.dto.request.ResetPasswordRequest
import com.billeteravirtual.backend.dto.request.ValidarEmailRequest
import com.billeteravirtual.backend.dto.response.AuthResponse
import com.billeteravirtual.backend.dto.response.UsuarioResponse
import com.billeteravirtual.backend.service.AuthService
import com.billeteravirtual.backend.service.UsuarioService
import jakarta.servlet.http.HttpServletRequest
import jakarta.servlet.http.HttpServletResponse
import jakarta.servlet.http.HttpSession
import jakarta.validation.Valid
import org.springframework.http.HttpStatus
import org.springframework.http.ResponseEntity
import org.springframework.security.core.annotation.AuthenticationPrincipal
import org.springframework.security.core.context.SecurityContextHolder
import org.springframework.security.core.userdetails.UserDetails
import org.springframework.web.bind.annotation.GetMapping
import org.springframework.web.bind.annotation.PostMapping
import org.springframework.web.bind.annotation.RequestBody
import org.springframework.web.bind.annotation.RequestMapping
import org.springframework.web.bind.annotation.RestController

@RestController
@RequestMapping("/api/auth")
class AuthController(
    private val authService: AuthService,
    private val usuarioService: UsuarioService
) {
    @PostMapping("/registro")
    fun registrar(@Valid @RequestBody request: RegistroRequest): ResponseEntity<AuthResponse> {
        val response = authService.registrar(request)
        return if (response.success) ResponseEntity.status(HttpStatus.CREATED).body(response)
        else ResponseEntity.badRequest().body(response)
    }

    @PostMapping("/validar-email")
    fun validarEmail(@Valid @RequestBody request: ValidarEmailRequest): ResponseEntity<AuthResponse> {
        val response = authService.validarEmail(request)
        return if (response.success) ResponseEntity.ok(response)
        else ResponseEntity.badRequest().body(response)
    }

    @PostMapping("/login")
    fun login(
        @Valid @RequestBody request: LoginRequest,
        httpRequest: HttpServletRequest,
        httpResponse: HttpServletResponse
    ): ResponseEntity<AuthResponse> {
        val response = authService.login(request)
        if (response.success) {
            val session: HttpSession = httpRequest.getSession(true)
            session.setAttribute("SPRING_SECURITY_CONTEXT", SecurityContextHolder.getContext())
        }
        return if (response.success) ResponseEntity.ok(response)
        else ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(response)
    }

    @PostMapping("/olvide-password")
    fun olvidePassword(@Valid @RequestBody request: OlvidePasswordRequest): ResponseEntity<AuthResponse> {
        val response = authService.olvidePassword(request)
        return ResponseEntity.ok(response)
    }

    @PostMapping("/reset-password")
    fun resetPassword(@Valid @RequestBody request: ResetPasswordRequest): ResponseEntity<AuthResponse> {
        val response = authService.resetPassword(request)
        return if (response.success) ResponseEntity.ok(response)
        else ResponseEntity.badRequest().body(response)
    }

    @GetMapping("/me")
    fun me(@AuthenticationPrincipal user: UserDetails): ResponseEntity<UsuarioResponse> {
        val usuario = usuarioService.obtenerUsuario(user.username)
            ?: return ResponseEntity.notFound().build()
        return ResponseEntity.ok(usuario)
    }
}
