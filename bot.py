import logging
import os
import uuid

import flask
import psycopg2
import cv2
import telebot
from pydub import AudioSegment
from telebot import types

TOKEN='5096179678:AAGu0J3Zejp1wk7MKwA6zJrGvemEXylnvDY'
DB_NAME='db7p2s49rgpa7v'
DB_USER='ynisucqnfhchco'
DB_PASSWORD='e7d0b9f747f46a8da294a0a7cca1202ee46ff1db2e3aa41bfc4b67709551bcba'
DB_HOST='ec2-54-73-147-133.eu-west-1.compute.amazonaws.com'

bot = telebot.TeleBot(TOKEN)

server = flask.Flask(__name__)


@server.route('/', methods=["GET"])
def index():
    bot.remove_webhook()
    bot.set_webhook('https://idrnd-test.herokuapp.com/')
    return "Hello from Heroku!", 200


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))

@bot.message_handler(content_types=['voice'])
def voice_handle(message):
    file_info = bot.get_file(message.voice.file_id)
    # downloaded_file = bot.download_file(file_info.file_path)
    audio = AudioSegment.from_ogg(file_info.file_path)
    audio_id = uuid.uuid4()
    audio.export(f'audio_message_{audio_id}.wav', format='wav', bitrate='16')
    file = None
    with open(f'audio_message_{audio_id}.wav', 'rb') as audio_file:
        conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO files(id, file) VALUES (DEFAULT,%s) RETURNING file", audio_file)
        file = cursor.fetchone()[0]
        conn.commit()
        conn.close()
    bot.reply_to(message, file)



#@server.route('/', methods=['POST'])
@bot.message_handler(content_types=['photo'])
def photo_handle(message):
    logging.Logger.log(f'{message}')
    file_info = bot.get_file(message.voice.file_id)
    img = cv2.imread(file_info.file_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    recognition = cv2.CascadeClassifier('frontalface.xml')

    results = recognition.detectMultiScale(gray, scaleFactor=2)

    if results:
        conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port='5432')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO files(id, file) VALUES (DEFAULT,%s) RETURNING file", file_info.file_path)
        file = cursor.fetchone()[0]
        conn.commit()
        conn.close()

        bot.reply_to(message, f'Найдено лицо, сохраняем {file}')
        return
    bot.reply_to(message, 'Лицо не найдено')
