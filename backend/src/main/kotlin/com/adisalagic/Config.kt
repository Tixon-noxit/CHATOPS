package com.adisalagic

import com.google.gson.annotations.SerializedName

data class Config(
    val token: String,
    @SerializedName("api_url") val apiUrl: String,
    val webhook: WebHookConfig
) {
    data class WebHookConfig(
        val url: String,
        val ip: String,
        val port: Int,
        val secretKey: String,
    )
}
