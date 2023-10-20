from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext, CallbackQueryHandler
from dotenv import load_dotenv
import os
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup

# Importa le funzioni dagli altri script
from EventoManager import *
from UserRegistration import *
from DatabaseConnection import *


load_dotenv()
TOKEN = os.environ.get('TOKEN')

def start(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    context.bot.send_message(
        chat_id=user_id,
        text="Ciao! Sono il GlabBot, il tuo assistente per la gestione degli eventi.\n"
             "Ecco cosa posso fare:\n"
             "- /creaevento: Crea un nuovo evento\n"
             "- /annulla: Annulla la creazione dell'evento in corso\n"
             "- /postcanale: Pubblica l'ultimo evento creato sul canale\n"
             "- /Registrazione Registrati se non sei iscritto\n"
             "Inizia inviandomi uno di questi comandi per iniziare!"
    )

def main() -> None:
    create_table()

    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start))
    

    # Aggiungi gli entry points e le ConversationHandler per eventi e registrazione
    
    conv_handler_eventi = ConversationHandler(
        entry_points=[CommandHandler('creaevento', start_create_event)],
        states={
            EVENT_NAME: [MessageHandler(Filters.text & ~Filters.command, collect_event_name)],
            EVENT_DESC: [MessageHandler(Filters.text & ~Filters.command, collect_event_desc)],
            EVENT_DATE: [MessageHandler(Filters.regex(r'^\d{2}-\d{2}-\d{4}$') & ~Filters.command, collect_event_date)],
            EVENT_POST: [MessageHandler(Filters.photo | Filters.command, collect_event_post)]
        },
        fallbacks=[CommandHandler('annulla', lambda update, context: ConversationHandler.END)]
    )
    conv_handler_registrazione = ConversationHandler(
        entry_points=[CommandHandler('registrazione', start_registration)],
        states={
            REGISTER: [MessageHandler(Filters.text & ~Filters.command, collect_full_name)],
            COLLECT_SKILLS: [MessageHandler(Filters.text & ~Filters.command, collect_skills)],
            CONFIRM_PUBLICATION: [MessageHandler(Filters.text & ~Filters.command, confirm_publication)],
        },
        fallbacks=[]
    )
   
    dispatcher.add_handler(conv_handler_eventi)
    dispatcher.add_handler(conv_handler_registrazione)
    # Aggiungi l'handler per il comando /postcanale
    dispatcher.add_handler(CommandHandler('postcanale', post_canale))
    dispatcher.add_handler(CallbackQueryHandler(post_event, pattern='post_canale'))



    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
