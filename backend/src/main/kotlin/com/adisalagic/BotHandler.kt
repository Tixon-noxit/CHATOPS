package com.adisalagic

import com.github.kotlintelegrambot.Bot
import com.github.kotlintelegrambot.dispatcher.Dispatcher
import com.github.kotlintelegrambot.dispatcher.callbackQuery
import com.github.kotlintelegrambot.dispatcher.command
import com.github.kotlintelegrambot.dispatcher.message
import com.github.kotlintelegrambot.entities.ParseMode
import kotlinx.coroutines.*

object BotHandler {
    enum class ContextType {
        ROLLBACK,
        SCALE,
        UPSCALE,
        RESTART
    }

    data class Context(val contextType: ContextType, val chatId: Long)

    private lateinit var bot: Bot
    private lateinit var api: Api
    private var contextArgs = emptyList<String>()
    private var currentContext: Context? = null
    private val botCoroutine = CoroutineScope(Job())

    private val dispatchers: Dispatcher.() -> Unit = {
        callbackQuery("yes") {
            botCoroutine.launch(Dispatchers.IO) {
                when (currentContext?.contextType) {
                    ContextType.ROLLBACK -> api.requestRollback(currentContext!!.chatId)
                    ContextType.SCALE -> {
                        val arg = contextArgs.getOrNull(0)?.toIntOrNull()
                        if (arg != null) {
                            if (arg == 0) {
                                bot.sendMessage(
                                    chatId = currentContext!!.chatId.tgid,
                                    "❌ Number must be greater or less than 0. *Operation canceled*",
                                    parseMode = ParseMode.MARKDOWN
                                )
                                currentContext = null
                            }
                            api.requestScale(arg, currentContext!!.chatId)
                        }
                    }

                    ContextType.UPSCALE -> {
                    }

                    ContextType.RESTART -> {}
                    null -> {}
                }
                currentContext = null
            }
        }
        callbackQuery("no") {
            if (callbackQuery.message != null)
                bot.sendMessage(chatId = callbackQuery.message!!.chat.id.tgid, "Cancelled")
        }
        command("start") {
            bot.sendMessage(message.chat.id.tgid, "Let's pretend we are registering you 😊")
            api.sendChatId(message.chat.id)
        }
        command("status") {
            api.requestStatus(message.chat.id)
        }
        command("rollback") {
            currentContext = Context(ContextType.ROLLBACK, chatId = message.chat.id)
            requestConfirmation()
        }
        command("scale") {
            currentContext = Context(ContextType.SCALE, chatId = message.chat.id)
            if (args.isEmpty()) {
//                bot.sendMessage(chatId = message.chat.id.tgid, "No arguments were provided. It's rather +N or -N")
                bot.sendMessage(chatId = message.chat.id.tgid, "Enter an integer to scale for")
                update.consume()
                return@command
            }
            contextArgs = args
            requestConfirmation()
        }
        message {
            if (currentContext?.contextType == ContextType.SCALE) {
                if (message.text?.contains("scale") == true) return@message
                val num = message
                    .text
                    ?.split(" ")
                    ?.get(0)
                    ?.toIntOrNull()
                if (num == null) {
                    bot.sendMessage(
                        chatId = message.chat.id.tgid,
                        "❌ Invalid argument, try again. Write 0 to cancel"
                    )
                    return@message
                }
                if (num == 0) {
                    bot.sendMessage(
                        chatId = message.chat.id.tgid,
                        "❌ Number must be greater or less than 0. *Operation canceled*",
                        parseMode = ParseMode.MARKDOWN
                    )
                    currentContext = null
                    return@message
                }
                requestConfirmation()
                contextArgs = listOf(num.toString())
            }
        }
    }

    fun start(config: Config) {
        api = Api(config)
        bot = defaultBot(config, dispatchers)
        bot.startPolling()
    }
}