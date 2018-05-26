from flask import Flask, request
import telebot, logging
from random import randint
import configparser
import markovify
import re
import spacy
from spacy.lang.fr.examples import sentences


app = Flask(__name__)

Config = configparser.ConfigParser()
Config.read('/config/config.ini')
key = Config.get('Main', 'key')
url = Config.get('Main', 'url')
master = Config.get('Main', 'master')
global bot
global percent
global violence
global nlp
global text_model
bot = telebot.TeleBot(key)
logger = telebot.logger
telebot.logger.setLevel(logging.INFO)
percent = 5
violence = False
nlp = spacy.load("fr_core_news_md")
with open("model.json", "r") as f:
  model_json = f.read()
  text_model = POSifiedText.from_json(model_json)


class POSifiedText(markovify.NewlineText):
    def word_split(self, sentence):
        return ["::".join((word.orth_, word.pos_)) for word in nlp(sentence)]

    def word_join(self, words):
        sentence = " ".join(word.split("::")[0] for word in words)
        return sentence

@app.route(url, methods=['GET', 'POST'])
def hook():
    if request.method == "POST":
        # retrieve the message in JSON and then transform it to Telegram object
        json_string = request.get_data()
        update = telebot.types.Update.de_json(json_string)
        if "edited_message" in json_string:
            return ''
        else:
            bot.process_new_messages([update.message])
            return ''


@bot.message_handler(commands=['setfun'])
def setfun(message):
    if str(message.from_user.id) == master:
      try:
          global percent
          percent = int(message.text.split()[1])
          bot.reply_to(message, "Fun set to " + str(percent) + "%, you crazy man.")
      except:
          bot.reply_to(message, "Damn, it doesn't work.")


@bot.message_handler(commands=['toggleviolence'])
def setfun(message):
    if str(message.from_user.id) == master:
      try:
          global violence
          violence = not violence
          if violence:
            bot.reply_to(message, "Violence activated")
          else:
            bot.reply_to(message, "Violence deactivated")
      except:
          bot.reply_to(message, "Damn, it doesn't work.")

@bot.message_handler(func=lambda message: True)
def fun(message):
    print(message.text)
    if (randint(1, 100) < percent):
      if violence : 
        bot.reply_to(text_model.make_sentence())
      else :
        bot.reply_to(text_model.make_sentence())
    return 'ok'

if __name__ == '__main__':
    app.run(port=9876, debug=True)