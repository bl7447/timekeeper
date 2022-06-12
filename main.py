import datetime, random

import requests
from telegram.ext import *
from constants import api_key, firebaseConfig
import pyrebase
from gcal import create_event_google, update_event_google, delete_event_google, read_google_events

#initialise connection to firebase
firebase = pyrebase.initialize_app(firebaseConfig)

db = firebase.database()

Name, Date, Time = range(3)


def start_command(update, context):
    chat_id = update.message.chat.id
    print(update.message.chat.id)
    print(update.message.from_user)
    db.child("users").child(chat_id).child("google").set({'sync': False})
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
    chat_id = update.message.chat.id
    events = db.child("users").child(chat_id).child("events").get()
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
    chat_id = update.message.chat.id
    data['time'] = update.message.text
    date_formatted = datetime.date(data['year'], data['month'], data['day'])
    reply = f"{data['name']} scheduled for {date_formatted} at {data['time']}hrs.\nThe event has been created successfully!"
    google_enabled = db.child("users").child(chat_id).child("google").get().val()['sync']
    if google_enabled:
        event_id = create_event_google(data['name'], data['year'], data['month'], data['day'], int(data['time'][0:2]), int(data['time'][2:]))
        reply += "\n Event added to Google Calendar. /google to disable."
        data['event_id'] = event_id
    db.child("users").child(chat_id).child("events").child(data['name']).set(data)
    update.message.reply_text(reply)
    return ConversationHandler.END


def cancel(update, context):
    update.message.reply_text("Cancelled.")
    return ConversationHandler.END


def update_command(update, context):
    chat_id = update.message.chat.id
    global data
    data = {'name': '', 'day': 0, 'month': 0, 'year': 0, 'time': ''}
    events = db.child("users").child(chat_id).child("events").order_by_child("name").get()
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
    chat_id = update.message.chat.id
    data['name'] = update.message.text
    current_day = db.child('users').child(chat_id).child("events").child(data['name']).get().val()['day']
    data['day'] = current_day
    current_month = db.child('users').child(chat_id).child("events").child(data['name']).get().val()['month']
    data['month'] = current_month
    current_year = db.child('users').child(chat_id).child("events").child(data['name']).get().val()['year']
    data['year'] = current_year
    date_formatted = datetime.date(current_year, current_month, current_day)
    update.message.reply_text(f"Current date: {date_formatted}\nEnter the updated date in DDMMYYYY format or enter 'skip' if there are no changes. (/cancel to cancel)")
    return Date


def updatedate(update, context):
    chat_id = update.message.chat.id
    date_input = update.message.text
    if date_input != 'skip':
        y = int(date_input[4:])
        data['year'] = y
        m = int(date_input[2:4])
        data['month'] = m
        d = int(date_input[:2])
        data['day'] = d
        db.child('users').child(chat_id).child("events").child(data['name']).update({"day": d})
        db.child('users').child(chat_id).child("events").child(data['name']).update({"month": m})
        db.child('users').child(chat_id).child("events").child(data['name']).update({"year": y})
    current_time = db.child('users').child(chat_id).child("events").child(data['name']).get().val()['time']
    data['time'] = current_time
    update.message.reply_text(f"Current time: {current_time}\nEnter the updated time in 24H format or enter 'skip' if there are no changes. (/cancel to cancel)")
    return Time


def updatetime(update, context):
    chat_id = update.message.chat.id
    option = update.message.text
    if option != 'skip':
        db.child('users').child(chat_id).child("events").child(data['name']).update({"time": option})
        data['time'] = option
    google_enabled = db.child("users").child(chat_id).child("google").get().val()['sync']
    if google_enabled:
        event_id = db.child("users").child(chat_id).child("events").child(data['name']).get().val()['event_id']
        update_event_google(event_id, data['name'], data['year'], data['month'], data['day'], int(data['time'][:2]),
                            int(data['time'][2:]))
    update.message.reply_text("The event has been updated successfully!")
    return ConversationHandler.END


def delete_command(update, context):
    chat_id = update.message.chat.id
    global data
    data = {'name': '', 'day': 0, 'month': 0, 'year': 0, 'time': ''}
    events = db.child("users").child(chat_id).child("events").order_by_child("name").get()
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


def delete_name(update, context):
    data['name'] = update.message.text
    update.message.reply_text(f"Are you sure you want to delete {data['name']}? Enter 'y' to confirm.")
    return Date


def deleteoption(update, context):
    chat_id = update.message.chat.id
    option = update.message.text
    if option == 'y':
        google_enabled = db.child("users").child(chat_id).child("google").get().val()['sync']
        if google_enabled:
            event_id = db.child("users").child(chat_id).child("events").child(data['name']).get().val()['event_id']
            delete_event_google(event_id)
        db.child("users").child(chat_id).child("events").child(data['name']).remove()
        update.message.reply_text("Event has been removed.")
    return ConversationHandler.END


notification_list = []


def print_something(context):
    print(datetime.datetime.now())
    if notification_list:
        for j in range(len(notification_list)):
            x = requests.get('https://type.fit/api/quotes')
            r = x.json()
            index = random.randint(0, len(r) - 1)
            text = r[index]['text']
            author = r[index]['author']
            quote = f'"{text}" - {author}'
            today = datetime.date.today()
            events = db.child("users").child(notification_list[j]).child("events").get()
            events_string = "Good morning! Here are your events in the next 14 days:"
            i = 1

            for event in events:
                d = event.val()['day']
                m = event.val()['month']
                y = event.val()['year']
                date_formatted = datetime.date(y, m, d)
                if (date_formatted - today) <= datetime.timedelta(days=14):
                    events_string += f"\n{i}. {event.val()['name']} - {date_formatted} at {event.val()['time']}hrs"
                    i += 1
            context.bot.send_message(notification_list[j], quote)
            context.bot.send_message(notification_list[j], events_string)
            print(quote)


def daily_notif(update, context):
    print("daily notifications activated.")
    update.message.reply_text("Daily notifications activated. use /stopdaily to deactivate.")
    chat_id = update.message.chat.id
    if chat_id not in notification_list:
        notification_list.append(chat_id)
    job_queue.run_repeating(callback=print_something, interval=10)
    # job_queue.start()


def daily_notif_stop(update, context):
    chat_id = update.message.chat.id
    if chat_id in notification_list:
        notification_list.remove(chat_id)
    update.message.reply_text("Daily notifications stopped.")
    print("daily notifications stopped.")


def toggle_google(update, context):
    chat_id = update.message.chat.id
    current_setting = db.child("users").child(chat_id).child("google").get().val()['sync']
    print(current_setting)
    if current_setting:
        db.child("users").child(chat_id).child("google").set({'sync': False})
        update.message.reply_text("Google Calendar sync has been disabled.")
    else:
        update.message.reply_text("Syncing Google Calendar events...")
        db.child("users").child(chat_id).child("google").set({'sync': True})
        google_events = read_google_events()
        for event in google_events:
            db.child("users").child(chat_id).child("events").child(event['name']).set(event)
        update.message.reply_text("Google Calendar sync has been enabled.")


def google_status(update, context):
    chat_id = update.message.chat.id
    current_setting = db.child("users").child(chat_id).child("google").get().val()['sync']
    if current_setting:
        update.message.reply_text("Google Calendar sync is on. /google to turn off.")
    else:
        update.message.reply_text("Google Calendar sync is off. /google to turn on.")


def check_past(context):
    today = datetime.date.today()
    users = db.child("users").get()
    for user in users.each():
        chat_id = user.key()
        events = db.child("users").child(chat_id).child("events").get()
        for event in events:
            d = event.val()['day']
            m = event.val()['month']
            y = event.val()['year']
            date_formatted = datetime.date(y, m, d)
            if (date_formatted - today) <= datetime.timedelta(days=0):
                print(f"{event.val()['name']} has already past.")
                db.child("users").child(chat_id).child("events").child(event.val()['name']).remove()


def error(update, context):
    print(f"Update {update} caused error {context.error}")


print("Starting bot...")
# updater = Updater(api_key, use_context=True)
updater = Updater(api_key)

dp = updater.dispatcher

dp.add_handler(CommandHandler("start", start_command))
dp.add_handler(CommandHandler("help", help_command))
dp.add_handler(CommandHandler("view", view_command))
conv_handler = ConversationHandler(
    entry_points=[CommandHandler("create", create_command)],
    states={
        Name: [MessageHandler(filters=Filters.text & ~Filters.command, callback=name)],
        Date: [MessageHandler(filters=Filters.text & ~Filters.command, callback=date)],
        Time: [MessageHandler(filters=Filters.text & ~Filters.command, callback=time)]
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)
dp.add_handler(conv_handler)

conv_handler2 = ConversationHandler(
    entry_points=[CommandHandler("edit", update_command)],
    states={
        Name: [MessageHandler(filters=Filters.text & ~Filters.command, callback=updatename)],
        Date: [MessageHandler(filters=Filters.text & ~Filters.command, callback=updatedate)],
        Time: [MessageHandler(filters=Filters.text & ~Filters.command, callback=updatetime)]
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)
dp.add_handler(conv_handler2)

conv_handler3 = ConversationHandler(
    entry_points=[CommandHandler("delete", delete_command)],
    states={
        Name: [MessageHandler(filters=Filters.text & ~Filters.command, callback=delete_name)],
        Date: [MessageHandler(filters=Filters.text & ~Filters.command, callback=deleteoption)]
    },
    fallbacks=[CommandHandler("cancel", cancel)]
)
dp.add_handler(conv_handler3)

job_queue = JobQueue()
job_queue.set_dispatcher(dp)
job_queue.run_daily(callback=check_past, days=(0, 1, 2, 3, 4, 5, 6), time=datetime.time(0, 0, 0, 0))
job_queue.start()
dp.add_handler(CommandHandler("daily", daily_notif))
dp.add_handler(CommandHandler("stopdaily", daily_notif_stop))
dp.add_handler(CommandHandler("google", toggle_google))
dp.add_handler(CommandHandler("googlestatus", google_status))
dp.add_handler(MessageHandler(Filters.text, handle_message))

dp.add_error_handler(error)

updater.start_polling()
# job_queue.start()
updater.idle()
