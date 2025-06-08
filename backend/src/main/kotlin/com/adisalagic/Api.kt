package com.adisalagic

import com.adisalagic.objects.ChatTgId
import com.adisalagic.objects.ScaleInstances
import com.google.gson.reflect.TypeToken
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import java.io.IOException
import java.lang.reflect.Type

class Api(config: Config) {
    private val client = OkHttpClient()
    private val baseUrl = config.apiUrl

    fun sendChatId(chatId: Long) {
        Request.Builder()
            .url("$baseUrl/telegram/add_chat_id")
            .post(ChatTgId(chatId).json.toRequestBody("application/json".toMediaTypeOrNull()))
            .header("Authorization", "secret_key_123")
            .build()
            .execute<Unit>()
    }

    fun requestStatus(chatId: Long) {
        Request.Builder()
            .url("$baseUrl/status")
            .post(ChatTgId(chatId).json.toRequestBody("application/json".toMediaTypeOrNull()))
            .header("Authorization", "secret_key_123")
            .build()
            .execute<Unit>()
    }

    fun requestRollback(chatId: Long) {
        Request.Builder()
            .url("$baseUrl/rollback")
            .header("Authorization", "secret_key_123")
            .post(ChatTgId(chatId).json.toRequestBody("application/json".toMediaTypeOrNull()))
            .build()
            .execute<Unit>()
    }

    fun requestScale(instances: Int, chatId: Long) {
        Request.Builder()
            .url("$baseUrl/scale")
            .post(ScaleInstances(instances, chatId).json.toRequestBody("application/json".toMediaTypeOrNull()))
            .header("Authorization", "secret_key_123")
            .build()
            .execute<Unit>()
    }

    private inline fun <reified T> Request.execute(): Result<T> {
        val call = client.newCall(this)
        try {
            call.execute().use {
                return if (it.body != null) {
                    Result.success(it.body!!.string().toAPIClass(genericType<T>()))
                } else if (!it.isSuccessful) {
                    Result.failure(IOException("Response code was not is range 200-299"))
                } else {
                    Result.failure(IOException())
                }
            }
        } catch (e: Exception) {
            e.printStackTrace()
            return Result.failure(e)
        }
    }

    private inline fun <reified T : Any> String.toAPIClass(clazz: Type): T {
        return gson.fromJson(this, clazz)
    }

    private inline fun <reified T> genericType() = object : TypeToken<T>() {}.type
}