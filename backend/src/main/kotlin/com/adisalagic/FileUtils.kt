package com.adisalagic

import com.google.gson.Gson
import com.google.gson.GsonBuilder
import java.io.File

val gson: Gson = GsonBuilder().serializeNulls().create()

val String.asFile: File get() = File(this)

inline fun <reified T> File.read(): T {
    return gson.fromJson(this.readText(), T::class.java)
}