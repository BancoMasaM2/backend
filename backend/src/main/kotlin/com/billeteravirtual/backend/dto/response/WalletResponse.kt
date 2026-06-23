package com.billeteravirtual.backend.dto.response

import java.math.BigDecimal

data class WalletResponse(
    val usuario: String,
    val cuentas: List<CuentaResponse>
)

data class CuentaResponse(
    val moneda: String,
    val saldo: BigDecimal,
    val alias: String
)
