#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import sys
import time
import threading

import telegramHandler
import wikiScanner

logging.basicConfig(format='[%(levelname)s] %(name)s: %(message)s',level=logging.DEBUG)
logger = logging.getLogger("main")

logger.info('starting wikiTrendsBot')

logger.debug('creating wiki scanner thread')
scannerThread = wikiScanner.wikiScanner()
scannerThread.daemon = True
scannerThread.start()

logger.debug('creating telegram-handler thread')
telegramThread = telegramHandler.telegramHandler(scannerThread)
telegramThread.daemon = True
telegramThread.start()

while True:
    try:
        time.sleep(3)
    except KeyboardInterrupt:
        logger.info('Exiting...')
        sys.exit()
    except:
        raise

