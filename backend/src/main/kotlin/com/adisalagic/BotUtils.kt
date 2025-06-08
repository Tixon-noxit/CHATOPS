package com.adisalagic

import com.github.kotlintelegrambot.Bot
import com.github.kotlintelegrambot.bot
import com.github.kotlintelegrambot.dispatch
import com.github.kotlintelegrambot.dispatcher.Dispatcher
import com.github.kotlintelegrambot.dispatcher.handlers.CommandHandlerEnvironment
import com.github.kotlintelegrambot.dispatcher.handlers.HandleMessage
import com.github.kotlintelegrambot.dispatcher.handlers.MessageHandlerEnvironment
import com.github.kotlintelegrambot.entities.*
import com.github.kotlintelegrambot.entities.keyboard.InlineKeyboardButton
import com.github.kotlintelegrambot.logging.LogLevel
import com.github.kotlintelegrambot.webhook

fun defaultBot(config: Config, createCommands: Dispatcher.() -> Unit): Bot {
    return bot {
        this.token = config.token
        dispatch(createCommands)
        this.logLevel = LogLevel.Error
        webhook {
            url = config.webhook.url
            secretToken = config.webhook.secretKey
            allowedUpdates = listOf("message")
        }

    }
}

val Long.tgid: ChatId get() = ChatId.fromId(this)

val <T> T.json: String
    get() = gson.toJson(this)

private fun reqConfirmation(update: Update, bot: Bot, message: Message) {
    if (update.callbackQuery == null) {
        bot.sendMessage(
            message.chat.id.tgid, "*ARE YOU SURE?*", parseMode = ParseMode.MARKDOWN_V2 , replyMarkup = InlineKeyboardMarkup.create(
                listOf(
                    listOf(
                        InlineKeyboardButton.CallbackData("Yes", "yes"),
                        InlineKeyboardButton.CallbackData("No", "no")
                    )
                )
            )
        )
    }
}

fun CommandHandlerEnvironment.requestConfirmation() {
    reqConfirmation(update, bot, message)
}

fun MessageHandlerEnvironment.requestConfirmation() {
    reqConfirmation(update, bot, message)
}
