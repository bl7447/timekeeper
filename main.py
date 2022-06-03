import datetime
from telegram.ext import *
from constants import api_key, firebaseConfig
import pyrebase


#initialise connection to firebase
firebase = pyrebase.initialize_app(firebaseConfig)

db = firebase.database()

Name, Date, Time = range(3)


def start_command(update, context):
    print(update.message.chat.id)
    print(update.message.from_user)
    update.message.reply_text("Type /help to get started!")


def help_command(update, context):
    print(update.message.chat.id)
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
    chatid = update.message.chat.id
    events = db.child("users").child(chatid).child("events").order_by_child("date").get()
    events_string = "Here are your scheduled events:"
    i = 1
    for event in events:
        d = event.val()['day']
        m = event.val()['month']
        y = event.val()['year']
        date_formatted = datetime.date(y, m, d)
        events_string += f"\n{i}. {event.val()['name']} - {date_formatted} at {event.val()['time']}hrs"
        i += 1
    update.message.reply_text(events_string)


def create_command(update, context):
    global data
    data = {'name': '', 'day': 0, 'month': 0, 'year': 0, 'time': ''}
    update.message.reply_text("Enter the event name! (/cancel to cancel)")
    return Name


def name(update, context):
    data['name'] = update.message.text
    update.message.reply_text(f"Okay, I need more details about {data['name']}!\nEnter the date of the event in DDMMYYYY format. (/cancel to cancel)")
    return Date


def date(update, context):
    date_input = update.message.text
    y = int(date_input[4:])
    m = int(date_input[2:4])
    d = int(date_input[:2])
    data['day'] = d
    data['month'] = m
    data['year'] = y
    date_formatted = datetime.date(y, m, d)
    update.message.reply_text(f"Ok, The date will be on {date_formatted}!\nEnter the time of the event in 24H format! (/cancel to cancel)")
    return Time


def time(update, context):
    chatid = update.message.chat.id
    data['time'] = update.message.text
    db.child("users").child(chatid).child("events").child(data['name']).set(data)
    date_formatted = datetime.date(data['year'], data['month'], data['day'])
    update.message.reply_text(f"{data['name']} scheduled for {date_formatted} at {data['time']}hrs.\nThe event has been created successfully!")
    return ConversationHandler.END


def cancel(update, context):
    update.message.reply_text("Cancelled.")
    return ConversationHandler.END


def update_command(update, context):
    chatid = update.message.chat.id
    global data
    data = {'name': '', 'day': 0, 'month': 0, 'year': 0, 'time': ''}
    events = db.child("users").child(chatid).child("events").order_by_child("name").get()
    events_string = "Enter the name of an event to edit:"
    i = 1
    for event in events:
        d = event.val()['day']
        m = event.val()['month']
        y = event.val()['year']
        date_formatted = datetime.date(y, m, d)
        events_string += f"\n{i}. {event.val()['name']} - {date_formatted} at {event.val()['time']}hrs"
        i += 1
    events_string += "\n(/cancel to cancel)"
    update.message.reply_text(events_string)
    return Name


def updatename(update, context):
    chatid = update.message.chat.id
    data['name'] = update.message.text
    current_day = db.child('users').child(chatid).child("events").child(data['name']).get().val()['day']
    current_month = db.child('users').child(chatid).child("events").child(data['name']).get().val()['month']
    current_year = db.child('users').child(chatid).child("events").child(data['name']).get().val()['year']
    date_formatted = datetime.date(current_year, current_month, current_day)
    update.message.reply_text(f"Current date: {date_formatted}\nEnter the updated date in DDMMYYYY format or enter 'skip' if there are no changes. (/cancel to cancel)")
    return Date


def updatedate(update, context):
    chatid = update.message.chat.id
    date_input = update.message.text
    if date_input != 'skip':
        y = int(date_input[4:])
        m = int(date_input[2:4])
        d = int(date_input[:2])
        db.child('users').child(chatid).child("events").child(data['name']).update({"day": d})
        db.child('users').child(chatid).child("events").child(data['name']).update({"month": m})
        db.child('users').child(chatid).child("events").child(data['name']).update({"year": y})
    current_time = db.child('users').child(chatid).child("events").child(data['name']).get().val()['time']
    update.message.reply_text(f"Current time: {current_time}\nEnter the updated time in 24H format or enter 'skip' if there are no changes. (/cancel to cancel)")
    return Time


def updatetime(update, context):
    chatid = update.message.chat.id
    option = update.message.text
    if option != 'skip':
        db.child('users').child(chatid).child("events").child(data['name']).update({"time": option})
    update.message.reply_text("The event has been updated successfully!")
    return ConversationHandler.END


def delete_command(update, context):
    chatid = update.message.chat.id
    global data
    data = {'name': '', 'day': 0, 'month': 0, 'year': 0, 'time': ''}
    events = db.child("users").child(chatid).child("events").order_by_child("name").get()
    events_string = "Enter the name of an event to delete:"
    i = 1
    for event in events:
        d = event.val()['day']
        m = event.val()['month']
        y = event.val()['year']
        date_formatted = datetime.date(y, m, d)
        events_string += f"\n{i}. {event.val()['name']} - {date_formatted} at {event.val()['time']}hrs"
        i += 1
    events_string += "\n(/cancel to cancel)"
    update.message.reply_text(events_string)
    return Name


def deletename(update, context):
    data['name'] = update.message.text
    update.message.reply_text(f"Are you sure you want to delete {data['name']}? Enter 'y' to confirm.")
    return Date

def deleteoption(update, context):
    chatid = update.message.chat.id
    option = update.message.text
    if option == 'y':
        db.child("users").child(chatid).child("events").child(data['name']).remove()
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
        entry_points=[CommandHandler("edit", update_command)],
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
