from telegram.ext import *
from constants import api_key, firebaseConfig
import pyrebase


#initialise connection to firebase
firebase = pyrebase.initialize_app(firebaseConfig)

db = firebase.database()

Name, Date, Time = range(3)


def start_command(update, context):
    update.message.reply_text("Type /help to get started!")


def help_command(update, context):
    update.message.reply_text("""
Here are some commands you can use:
/view - View upcoming events.
/create - Creates a new scheduled event.
/edit - Edits and updates existing events.
/delete - Delete a scheduled event.""")


def handle_message(update, context):
    text = str(update.message.text).lower()
    if "hello" in text or "hi" in text:
        update.message.reply_text("Hi user!")
    else:
        update.message.reply_text("I don't understand, enter /help to see a list of commands!")


def view_command(update, context):
    events = db.child("events").order_by_child("date").get()
    events_string = "Here are your scheduled events:"
    i = 1
    for event in events:
        events_string += f"\n{i}. {event.val()['name']} - {event.val()['date']} at {event.val()['time']}hrs"
        i += 1
    update.message.reply_text(events_string)


def create_command(update, context):
    global data
    data = {'name': '', 'date': '', 'time': ''}
    update.message.reply_text("Enter the event name! (/cancel to cancel)")
    return Name


def name(update, context):
    data['name'] = update.message.text
    update.message.reply_text(f"Okay, I need more details about {data['name']}!\nEnter the date of the event in DDMMYYYY format. (/cancel to cancel)")
    return Date


def date(update, context):
    data['date'] = update.message.text
    update.message.reply_text(f"Ok, The date will be on {data['date']}!\nEnter the time of the event in 24H format! (/cancel to cancel)")
    return Time


def time(update, context):
    data['time'] = update.message.text
    db.child("events").child(data['name']).set(data)
    update.message.reply_text(f"{data['name']} scheduled for {data['date']} at {data['time']}hrs.\nThe event has been created successfully!")
    return ConversationHandler.END


def cancel(update, context):
    update.message.reply_text("Cancelled.")
    return ConversationHandler.END


def update_command(update, context):
    global data
    data = {'name': '', 'date': '', 'time': ''}
    events = db.child("events").order_by_child("name").get()
    events_string = "Enter the name of an event to update:"
    i = 1
    for event in events:
        events_string += f"\n{i}. {event.val()['name']}"
        i += 1
    events_string += "\n(/cancel to cancel)"
    update.message.reply_text(events_string)
    return Name


def updatename(update, context):
    data['name'] = update.message.text
    current_date = db.child("events").child(data['name']).get().val()['date']
    update.message.reply_text(f"Current date: {current_date}\nEnter the updated date in DDMMYYYY format or enter 'skip' if there are no changes. (/cancel to cancel)")
    return Date


def updatedate(update, context):
    option = update.message.text
    if option != 'skip':
        db.child("events").child(data['name']).update({"date": option})
    current_time = db.child("events").child(data['name']).get().val()['time']
    update.message.reply_text(f"Current time: {current_time}\nEnter the updated time in 24H format or enter 'skip' if there are no changes. (/cancel to cancel)")
    return Time


def updatetime(update, context):
    option = update.message.text
    if option != 'skip':
        db.child("events").child(data['name']).update({"time": option})
    update.message.reply_text("The event has been updated successfully!")
    return ConversationHandler.END


def delete_command(update, context):
    global data
    data = {'name': '', 'date': '', 'time': ''}
    events = db.child("events").order_by_child("name").get()
    events_string = "Enter the name of an event to delete:"
    i = 1
    for event in events:
        events_string += f"\n{i}. {event.val()['name']}"
        i += 1
    events_string += "\n(/cancel to cancel)"
    update.message.reply_text(events_string)
    return Name


def deletename(update, context):
    data['name'] = update.message.text
    update.message.reply_text(f"Are you sure you want to delete {data['name']}? Enter 'y' to confirm.")
    return Date

def deleteoption(update, context):
    option = update.message.text
    if option == 'y':
        db.child("events").child(data['name']).remove()
        update.message.reply_text("Event has been removed.")
    return ConversationHandler.END

def error(update, context):
    print(f"Update {update} caused error {context.error}")


def main():
    print("Starting bot...")
    updater = Updater(api_key, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start_command))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("view", view_command))
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("create", create_command)],
        states={
            Name : [MessageHandler(filters=Filters.text & ~Filters.command, callback=name)],
            Date : [MessageHandler(filters=Filters.text & ~Filters.command, callback=date)],
            Time : [MessageHandler(filters=Filters.text & ~Filters.command, callback=time)]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    dp.add_handler(conv_handler)

    conv_handler2 = ConversationHandler(
        entry_points=[CommandHandler("update", update_command)],
        states={
            Name : [MessageHandler(filters=Filters.text & ~Filters.command, callback=updatename)],
            Date : [MessageHandler(filters=Filters.text & ~Filters.command, callback=updatedate)],
            Time : [MessageHandler(filters=Filters.text & ~Filters.command, callback=updatetime)]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    dp.add_handler(conv_handler2)

    conv_handler3 = ConversationHandler(
        entry_points=[CommandHandler("delete", delete_command)],
        states={
            Name : [MessageHandler(filters=Filters.text & ~Filters.command, callback=deletename)],
            Date: [MessageHandler(filters=Filters.text & ~Filters.command, callback=deleteoption)]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    dp.add_handler(conv_handler3)

    dp.add_handler(MessageHandler(Filters.text, handle_message))

    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()


main()
