import logging
import os
import uuid
from urllib.request import urlretrieve

import flask
import psycopg2
import cv2
import telebot
from flask import request
from pydub import AudioSegment
from telebot import types

TOKEN='5096179678:AAGu0J3Zejp1wk7MKwA6zJrGvemEXylnvDY'
DB_NAME='db7p2s49rgpa7v'
DB_USER='ynisucqnfhchco'
DB_PASSWORD='e7d0b9f747f46a8da294a0a7cca1202ee46ff1db2e3aa41bfc4b67709551bcba'
DB_HOST='ec2-54-73-147-133.eu-west-1.compute.amazonaws.com'

bot = telebot.TeleBot(TOKEN)

server = flask.Flask(__name__)

@server.route('/', methods=["POST"])
def get_message():
    json_string = flask.request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    message = request.json.get('message')
    print(message)
    photo = message.get('photo')
    if photo:
        file_id = photo[2].get('file_id')
        file_info = bot.get_file(file_id)
        photo = bot.download_file(file_info.file_path)
        with open(f'photo_{file_id}.jpg', 'wb') as f:
            f.write(photo)
        img = cv2.imread(f'photo_{file_id}.jpg')
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        recognition = cv2.CascadeClassifier('frontalface.xml')

        results = recognition.detectMultiScale(gray, scaleFactor=1.5)

        if len(results):
            bot.send_message(message.get('chat').get('id'), 'Лицо найдено, сохраняем')
            return 'Ok', 200
        bot.send_message(message.get('chat').get('id'), 'Лицо не найдено')
    voice = message.get('voice')
    if voice:
        file_id = voice.get('file_id')
        file_info = bot.get_file(file_id)
        voice = bot.download_file(file_info.file_path)
        with open(f'audio_message_{file_id}.ogg', 'wb') as f:
            f.write(voice)
        AudioSegment.ffprobe = "ffmpeg\\fftools\\ffprobe.c"
        audio = AudioSegment.from_ogg(f'audio_message_{file_id}.ogg')
        audio.export(f'audio_message_{file_id}.wav', format='wav', bitrate='256')
        with open(f'audio_message_{file_id}.wav', 'rb') as audio_file:
            bot.send_audio(message.get('chat').get('id'), audio_file)
    return 'OK', 200


@server.route('/', methods=["GET"])
def index():
    return "ID R%D test", 200


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))

