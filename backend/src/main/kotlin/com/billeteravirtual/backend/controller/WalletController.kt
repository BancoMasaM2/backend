package com.billeteravirtual.backend.controller

import com.billeteravirtual.backend.dto.response.MovimientoResponse
import com.billeteravirtual.backend.dto.response.WalletResponse
import com.billeteravirtual.backend.service.WalletService
import org.springframework.http.ResponseEntity
import org.springframework.security.core.annotation.AuthenticationPrincipal
import org.springframework.security.core.userdetails.UserDetails
import org.springframework.web.bind.annotation.GetMapping
import org.springframework.web.bind.annotation.RequestMapping
import org.springframework.web.bind.annotation.RestController

@RestController
@RequestMapping("/api/wallet")
class WalletController(
    private val walletService: WalletService
) {
    @GetMapping("/estado")
    fun obtenerEstado(@AuthenticationPrincipal user: UserDetails): ResponseEntity<WalletResponse> {
        val wallet = walletService.obtenerEstado(user.username)
            ?: return ResponseEntity.notFound().build()
        return ResponseEntity.ok(wallet)
    }

    @GetMapping("/movimientos")
    fun obtenerMovimientos(@AuthenticationPrincipal user: UserDetails): ResponseEntity<List<MovimientoResponse>> {
        val movimientos = walletService.obtenerMovimientos(user.username)
        return ResponseEntity.ok(movimientos)
    }
}
