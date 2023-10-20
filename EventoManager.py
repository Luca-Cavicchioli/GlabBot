import sqlite3
import os
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import MessageHandler, Filters, ConversationHandler, CallbackContext, CallbackQueryHandler

EVENT_NAME, EVENT_DESC, EVENT_DATE, EVENT_POST = range(4)

#load_dotenv()
TOKEN = os.environ.get('TOKEN')





def save_image_locally(photo):
    file_id = photo.file_id
    file_path = f"images/{file_id}.jpg"

    if not os.path.exists("images"):
        os.makedirs("images")

    photo.download(file_path)
    return file_path

def start_create_event(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Benvenuto nella creazione di eventi!\nInizia inviandomi il nome dell'evento.")
    return EVENT_NAME

def collect_event_name(update: Update, context: CallbackContext) -> int:
    context.user_data['event_name'] = update.message.text
    update.message.reply_text("Ottimo! Ora inviami una breve descrizione dell'evento.")
    return EVENT_DESC

def collect_event_desc(update: Update, context: CallbackContext) -> int:
    context.user_data['event_desc'] = update.message.text
    update.message.reply_text("Data dell'evento (DD-MM-YYYY):")
    return EVENT_DATE

def collect_event_date(update: Update, context: CallbackContext) -> int:
    context.user_data['event_date'] = update.message.text
    update.message.reply_text("Ottimo! Infine, inviami una locandina per l'evento (opzionale), altrimenti digita /salta.")
    return EVENT_POST

def collect_event_post(update: Update, context: CallbackContext) -> int:
    if update.message.text == "/salta":
        context.user_data['event_post'] = None
    else:
        if update.message.photo:
            photo = update.message.photo[-1].get_file()
            file_path = save_image_locally(photo)
            context.user_data['event_post'] = file_path
            update.message.reply_text(f"Immagine salvata: {file_path}")
        else:
            update.message.reply_text("Formato non valido. Inviami una foto valida o digita /salta.")
            return EVENT_POST

    conn = sqlite3.connect('eventi.sqlite')
    cursor = conn.cursor()

    user_id = update.message.from_user.id
    event_name = context.user_data['event_name']
    event_desc = context.user_data['event_desc']
    event_date = context.user_data['event_date']
    event_photo_path = context.user_data.get('event_post')

    cursor.execute('INSERT INTO events (user_id, event_name, event_desc, event_date, event_photo_path) VALUES (?, ?, ?, ?, ?)',
                   (user_id, event_name, event_desc, event_date, event_photo_path))
    conn.commit()
    conn.close()

    summary = f"Evento: {event_name}\nDescrizione: {event_desc}\nData: {event_date}"
    if event_photo_path:
        update.message.reply_text(summary, reply_markup=markup_with_post_button())
    else:
        update.message.reply_text(summary, reply_markup=markup_with_post_button())

    return ConversationHandler.END

def post_canale(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    event = get_last_event(user_id)
    
    if event:
        send_event_to_channel(update, context, event)
    else:
        update.message.reply_text("Nessun evento da pubblicare.")


def markup_with_post_button():
    keyboard = [[InlineKeyboardButton("Posta sul Canale", callback_data="post_canale")]]
    return InlineKeyboardMarkup(keyboard)
def post_event(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    post_canale(update, context)


def get_last_event(user_id):
    conn = sqlite3.connect('eventi.sqlite')
    cursor = conn.cursor()

    cursor.execute('SELECT id, user_id, event_name, event_desc, event_date, event_photo_path FROM events WHERE user_id = ? ORDER BY id DESC LIMIT 1', (user_id,))
    event = cursor.fetchone()

    conn.close()

    return event

def send_event_to_channel(update: Update, context: CallbackContext, event):
    event_id, _, event_name, event_desc, event_date, event_photo_path = event
    event_date = datetime.strptime(event_date, '%d-%m-%Y').strftime('%d-%m-%Y')
    caption = f"Evento: {event_name}\nDescrizione: {event_desc}\nData: {event_date}"

    if event_photo_path:
        context.bot.send_photo(chat_id='@GlabBotTest', photo=open(event_photo_path, 'rb'), caption=caption)
    else:
        context.bot.send_message(chat_id='@GlabBotTest', text=caption)


