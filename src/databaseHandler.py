#!/usr/bin/python
# -*- coding: utf-8 -*-

import sqlite3
import logging
import datetime

logging.basicConfig(format='[%(levelname)s] %(name)s: %(message)s',level=logging.INFO)
logger = logging.getLogger("database-handler")

def init():
    logger.info("initializing registration database")
    con = sqlite3.connect('registration.db')
    db = con.cursor()
    db.execute("CREATE TABLE IF NOT EXISTS registrations( \
                    user TINYTEXT, \
                    language TINYTEXT, \
                    chatid TINYTEXT \
               )")
    con.commit()
    db.execute("CREATE TABLE IF NOT EXISTS trends( \
                language TINYTEXT, \
                trend TINYTEXT, \
                summary TEXT, \
                created TINYTEXT, \
                published TINYINT \
           )")
    con.commit()
    con.close()

def addUser(username, chatid, language='en'):
    logger.info("adding user " + username + " to database")
    con = sqlite3.connect('registration.db')
    db = con.cursor()
    db.execute("DELETE FROM registrations WHERE user=?",([username]))
    db.execute("INSERT INTO registrations (user,language,chatid) VALUES (?,?,?)",([username,language,chatid]))
    con.commit()
    con.close()
        
def removeUser(username):
    logger.info("removing user " + username + " from database")
    con = sqlite3.connect('registration.db')
    db = con.cursor()
    db.execute("DELETE FROM registrations WHERE user=?",([username]))
    con.commit()
    con.close()

def getUsers(language=False):
    con = sqlite3.connect('registration.db')
    con.row_factory = sqlite3.Row
    db = con.cursor()
    if language == False:
        db.execute("SELECT * FROM registrations")
    else:
        db.execute("SELECT * FROM registrations WHERE language=?",([language]))
    entries = db.fetchall()
    con.close()
    return entries
    
def getUserLang(chatid):
    con = sqlite3.connect('registration.db')
    con.row_factory = sqlite3.Row
    db = con.cursor()
    db.execute("SELECT * FROM registrations WHERE chatid=?",([str(chatid)]))
    entries = db.fetchall()
    con.close()
    return entries

def getLanguages():
    con = sqlite3.connect('registration.db')
    con.row_factory = sqlite3.Row
    db = con.cursor()
    db.execute("SELECT DISTINCT language FROM registrations")
    entries = db.fetchall()
    con.close()
    languages = []
    for entry in entries:
        languages.append(entry['language'])
    logger.debug('following languages are being queried: ' + str(set(languages)))
    return set(languages)

def getTrends(language='en', limit=3, unpublishedOnly=False):
    con = sqlite3.connect('registration.db')
    con.row_factory = sqlite3.Row
    db = con.cursor()
    if (unpublishedOnly):
        db.execute("SELECT * FROM trends WHERE language=? AND published='False' ORDER BY created DESC LIMIT ?",([str(language), limit]))
    else:
        db.execute("SELECT * FROM trends WHERE language=? ORDER BY created DESC LIMIT ?",([str(language), limit]))
    entries = db.fetchall()
    con.close()
    trends = []
    for entry in entries:
        trends.append(entry['trend'])
    logger.debug('following trends are being queried: ' + str(set(trends)))
    return set(trends)

def getTrend(title, language='en'):
    con = sqlite3.connect('registration.db')
    con.row_factory = sqlite3.Row
    db = con.cursor()
    db.execute("SELECT * FROM trends WHERE trend=? AND language=?",([str(title), str(language)]))
    entries = db.fetchall()
    con.close()
    return entries

def addTrend(language, trend, queryDate, summary):
    logger.debug("adding new trend for " + language + " in database")
    con = sqlite3.connect('registration.db')
    db = con.cursor()
    db.execute("INSERT INTO trends (language,trend,summary,created,published) VALUES (?,?,?,?,'False')",([language,trend,summary,queryDate]))
    con.commit()
    con.close()
    
def setNotified():
    logger.debug("setting everything to published in database")
    con = sqlite3.connect('registration.db')
    db = con.cursor()
    db.execute("UPDATE trends set published='True' WHERE 1")
    con.commit()
    con.close()

