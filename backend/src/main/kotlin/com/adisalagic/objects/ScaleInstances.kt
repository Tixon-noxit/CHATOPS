package com.adisalagic.objects

import com.google.gson.annotations.SerializedName

data class ScaleInstances(val instances: Int, @SerializedName("chat_id") val id: Long)
