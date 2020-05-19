from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters
import spacy
import backend
import requests
import os

os.environ["IEX_API_VERSION"] = "iexcloud-beta"
os.environ['IEX_TOKEN'] = 'sk_2c5c50e49ad74709a781b79770c1c9bc'
tele_TOKEN = "980569069:AAFeXOyqAT8p2L-YQAu-NlNgpEjxBmQjgTU"
updater = Updater(token=tele_TOKEN, use_context=True)
dispatcher = updater.dispatcher


def help_(update, context):
    response = "I support following commands:\n" \
               "/help - show this help message.\n" \
               "/gold - get real time gold price. \n" \
               "Try me.\n" \
               "You also can check stock price listed in NASDAQ."

    context.bot.send_message(chat_id=update.effective_chat.id, text=response)


start_handler = CommandHandler('help', help_)
dispatcher.add_handler(start_handler)


def gold_usd(update, context):
    gold_API = r"https://forex-data-feed.swissquote.com/public-quotes/bboquotes/instrument/XAU/USD"
    resp = requests.get(gold_API)
    bid = resp.json()[0]["spreadProfilePrices"][0]["bid"]
    ask = resp.json()[0]["spreadProfilePrices"][0]["ask"]
    message = "Real time Gold/USD:\nbid: {0}\nask: {1}".format(bid, ask)
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)


gold_handler = CommandHandler('gold', gold_usd)
dispatcher.add_handler(gold_handler)

nlp = spacy.load('en_core_web_md')

companies = []


def echo(update, context):
    global companies
    print(update.message.text)
    in_message = update.message.text.strip()
    if companies != list(nlp(in_message).ents) and len(nlp(in_message).ents) > 0:
        response = backend.price(nlp(in_message))
        companies = list(nlp(in_message).ents)
    elif 'description' in in_message.lower() or 'detail' in in_message.lower():
        response = backend.description(companies)
    elif 'news' in in_message.lower():
        response = backend.get_news(companies)
    if type(response) == list:
        if len(response)==0:
            context.bot.send_message(chat_id=update.effective_chat.id, text="No latest news.")
        else:
            for r in response:
                context.bot.send_message(chat_id=update.effective_chat.id, text=r)
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text=response)


echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
dispatcher.add_handler(echo_handler)

updater.start_polling()
# updater.stop()
