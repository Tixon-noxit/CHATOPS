package com.adisalagic

object Main {
    @JvmStatic
    fun main(args: Array<String>) {
        BotHandler.start("config.json".asFile.read())
    }
}