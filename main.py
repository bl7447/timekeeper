from pickle import TRUE
from telegram.ext import *

def sample_responses(input_text):
    user_message = str(input_text).lower()
    if user_message in ("hello", "hi"):
        return "Hello! I'm the TimeKeeper bot!"
    
    return "I don't understand!"

print("Starting bot...")

def start_command(update, context):
    update.message.reply_text("Type something to get started!")


def help_command(update, context):
    update.message.reply_text("I want to help but I don't know how...yet.")


def handle_message(update, context):
    text = str(update.messsage.text).lower()
    response = sample_responses(text)

    update.message.reply_text(response)


def error(update, context):
    print(f"Update {update} caused error {context.error}")


def main():
    updater = Updater("5313806860:AAF_jl1Otxbnq9Y7pDHbUPZMk6uudvqq5pc", use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start_command))
    dp.add_handler(CommandHandler("help", help_command))

    dp.add_handler(MessageHandler(Filters.text, handle_message))

    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()


main()
