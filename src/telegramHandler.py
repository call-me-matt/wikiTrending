#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import threading
import time
import logging
import requests

import databaseHandler

from telegram.ext import CallbackContext

from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters
from telegram.ext import JobQueue

TOKEN = os.environ['TELEGRAM_BOT_TOKEN'] 
WATCHDOG_INTERVAL_MIN = 60

logging.basicConfig(format='[%(levelname)s] %(name)s: %(message)s',level=logging.DEBUG)
logger = logging.getLogger("telegram-handler")

class telegramHandler (threading.Thread):

    def register(self, update, context):
        context.bot.send_message(chat_id=update.message.chat_id, text="Hello, " + update.message.from_user.first_name + ". I will inform you once per day about trends on Wikipedia. Currently I am watching the English version. In order to change the language, send the language code as follows: '/watch xx' according to xx.wikipedia.org. For example '/watch fr' for French or '/watch de' for German. To stop the reports, send /stop")
        databaseHandler.addUser(update.message.from_user.name,update.message.chat_id)
        self.scannerThread.check()

    def stop(self, update, context):
        context.bot.send_message(chat_id=update.message.chat_id, text="OK. I will stop sending updates. To reactivate, just send me a /start")
        databaseHandler.removeUser(update.message.from_user.name)

    def check_input(self, userInput):
        # check there are no special chars
        not_letters_or_digits = '!"\\%\'()*,;<>[]^ `{|}'
        filteredInput = str(userInput).translate(not_letters_or_digits)
        if (str(userInput) != filteredInput):
            return False
        # check its a valid wikipedia address
        request = requests.get('https://' + userInput + '.wikipedia.org')
        if request.status_code != 200:
            return False
        # everything seems fine
        return True

    def watch(self, update, context):
        if (len(context.args) != 1):
            user = databaseHandler.getUserLang(update.message.chat_id)
            if (len(user) == 0):
                self.register(update,context)
            else:
                context.bot.send_message(
                    chat_id=update.message.chat_id,
                    text="Currently you are watching " + str(user[0]['language']) + ".wikipedia.org. You can change the language according to xx.wikipedia.org: '/watch xx'. For example '/watch de' for German or 'watch fr' for French."
                )
        else:
            if (self.check_input(context.args[0])):
                context.bot.send_message(chat_id=update.message.chat_id, text="Allright. I will watch " + context.args[0] + ".wikipedia.org and notify you once per day about trending articles.")
                databaseHandler.addUser(update.message.from_user.name, update.message.chat_id, str(context.args[0]))
                self.scannerThread.check()
            else:
                context.bot.send_message(chat_id=update.message.chat_id, text="Sorry, I have problems understanding your inputs. Make sure it's a valid language code of wikipedia: en.wikipedia.org --> '/watch en'")

    def jobs(self, update, context):
        entries = databaseHandler.getEntries()
        if (not entries):
            context.bot.send_message(chat_id=update.message.chat_id, text="There are currently no active jobs.")
        else:
            for entry in entries:
                context.bot.send_message(chat_id=update.message.chat_id, text="User: " + str(entry['user']) + " (language: " + str(entry['language']) + ")")

    def echo(self, update, context):
        context.bot.send_message(chat_id=update.message.chat_id, text="🤓🙄 Please don't disturb me. I am observing.")
   
    def feedback(self, update, context):
        context.bot.send_message(chat_id=update.message.chat_id, text="For questions or feedback you can contact @KeinplanMAJORAN .")
   
    def sendNewTrends(self, context: CallbackContext):
        languages = databaseHandler.getLanguages()
        for language in languages:
            logger.debug('checking ' + str(language))
            trends = databaseHandler.getTrends(language=str(language), unpublishedOnly=True)
            if (trends != set()):
                logger.debug("Sending out new trends (" + language + ")")
                for trend in trends:
                    logger.debug("Sending out new trend " + str(trend))
                    usertable = databaseHandler.getUsers(language)
                    for user in usertable:
                        wikiData = databaseHandler.getTrend(str(trend), str(language))
                        message = "New Trend: <a href='https://" + str(language) + ".wikipedia.org/wiki/" + str(trend) + "'>" + str(wikiData[0]['trend']) + "</a>! " + str(wikiData[0]['summary'])
                        image = str(wikiData[0]['image'])
                        if (image != ''):
                            context.bot.send_photo(chat_id=str(user['chatid']), caption=str(message), photo=str(image), parse_mode='HTML')
                        else:
                            context.bot.send_message(chat_id=str(user['chatid']), text=str(message), parse_mode='HTML')
        logger.debug("Setting everything to notified")
        databaseHandler.setNotified()
        
    def __init__(self, scannerThread):
        global TOKEN
        global WATCHDOG_INTERVAL_MIN
        
        logger.info('starting telegram-handler')
        threading.Thread.__init__(self)
        
        self.scannerThread = scannerThread
        
        logger.debug("initializing telegram bot")
        self.updater = Updater(token=TOKEN, use_context=True)
        self.dispatcher = self.updater.dispatcher

        logger.debug("initializing registration database")
        databaseHandler.init()
        
        logger.debug('creating telegram-watchdog')
        watchdog = self.updater.job_queue.run_repeating(self.sendNewTrends, interval=WATCHDOG_INTERVAL_MIN*60, first=5)
      
    def run(self):
        start_handler = CommandHandler('start', self.register)
        self.dispatcher.add_handler(start_handler)

        stop_handler = CommandHandler('stop', self.stop)
        self.dispatcher.add_handler(stop_handler)
        
        watch_handler = CommandHandler('watch', self.watch, pass_args=True)
        self.dispatcher.add_handler(watch_handler)

        jobs_handler = CommandHandler('jobs', self.jobs)
        self.dispatcher.add_handler(jobs_handler)
        
        echo_handler = MessageHandler(Filters.text, self.echo)
        self.dispatcher.add_handler(echo_handler)
        
        unknown_handler = MessageHandler(Filters.command, self.feedback)
        self.dispatcher.add_handler(unknown_handler)

        self.updater.start_polling()
        #TODO: replace polling by webhook:
        #self.updater.start_webhook(listen='127.0.0.1', port=88, url_path='', cert=None, key=None, clean=False, bootstrap_retries=0, webhook_url=None, allowed_updates=None)

