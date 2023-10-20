import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext, CallbackQueryHandler



# Stati della conversazione
REGISTER, COLLECT_SKILLS, CONFIRM_PUBLICATION = range(3)

# Definiamo le competenze possibili
SKILLS = [
    "Fotografia",
    "Videomaking",
    "Scrittura",
    "Progettazione grafica",
    "Programmazione",
    "Musica",
    "Marketing",
    "Cucina",
    "Sport",
    "Arte",
    "Giardinaggio",
    "Lingue straniere",
    "Viaggi",
    "Elettronica",
    "Altro"
]

def start_registration(update: Update, context: CallbackContext) -> int:
    user_id = update.effective_user.id
    context.bot.send_message(
        chat_id=user_id,
        text="Benvenuto! Per registrarti, inserisci il tuo nome completo:"
    )
    return REGISTER

def collect_full_name(update: Update, context: CallbackContext) -> int:
    user_id = update.effective_user.id
    full_name = update.message.text
    print(f"Collected full name: {full_name}")  # Debugging line
    context.user_data['full_name'] = full_name

    conn = sqlite3.connect('eventi.sqlite')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    user = cursor.fetchone()

    if user:
        # User is already registered, update their information
        cursor.execute('UPDATE users SET full_name = ?, registration_status = ?, publication_permission = ? WHERE user_id = ?',
                       (full_name, 0, 0, user_id))
    else:
        # User is not registered, insert a new record
        cursor.execute('INSERT INTO users (user_id, full_name, registration_status, publication_permission) VALUES (?, ?, ?, ?)',
                       (user_id, full_name, 0, 0))

    conn.commit()
    conn.close()

    context.bot.send_message(
        chat_id=user_id,
        text="Ottimo! Ora, seleziona le tue competenze (puoi selezionarne più di una):",
        reply_markup=get_skills_keyboard()
    )
    return COLLECT_SKILLS


def collect_skills(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()

    user_id = update.effective_user.id
    skill = query.data  # The data from the button press is the skill

    if skill == 'finish':
        context.bot.send_message(
            chat_id=user_id,
            text="You have finished selecting skills.\n"
                 "Do you want to request publication permission on the channel? (Yes/No)"
        )
        return CONFIRM_PUBLICATION

    # Save the skill in the database
    conn = sqlite3.connect('eventi.sqlite')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO skills (user_id, skill_name) VALUES (?, ?)', (user_id, skill))
    conn.commit()
    conn.close()

    context.bot.send_message(
        chat_id=user_id,
        text=f"You have selected the skill: {skill}\n"
             "You can select more skills or press the 'Finish' button to complete the skill selection."
    )

    return COLLECT_SKILLS

def confirm_publication(update: Update, context: CallbackContext) -> int:
    user_id = update.effective_user.id
    response = update.message.text.lower()
    if response == "sì" or response == "si":
        # Invia una richiesta di certificazione all'amministratore
        admin_user_id = '481672513'  # Sostituisci con l'ID dell'amministratore
        admin_message = f"Richiesta di pubblicazione da:\nNome: {context.user_data['full_name']}\n" \
                        f"Competenze: {', '.join(context.user_data['skills'])}\n" \
                        f"ID Utente: {user_id}\n" \
                        f"Permettere la pubblicazione? (Rispondi con 'OK' per confermare)"
        context.bot.send_message(chat_id=admin_user_id, text=admin_message)

        context.bot.send_message(
            chat_id=user_id,
            text="La tua richiesta è stata inviata all'amministratore per la certificazione. "
                 "Riceverai una notifica non appena verrà processata."
        )
    else:
        context.bot.send_message(
            chat_id=user_id,
            text="Hai scelto di non richiedere il permesso di pubblicazione sul canale. "
                 "Se cambi idea, puoi farlo in qualsiasi momento."
        )

    return ConversationHandler.END

def get_skills_keyboard():
    keyboard = [[InlineKeyboardButton(skill, callback_data=skill)] for skill in SKILLS]
    keyboard.append([InlineKeyboardButton('Finish', callback_data='finish')])
    return InlineKeyboardMarkup(keyboard)
