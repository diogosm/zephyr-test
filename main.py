from flask import Flask, request, jsonify, render_template, url_for
from flask_compress import Compress
from functools import wraps
import os
import json
import time
import folium
import branca
import html
import folium.plugins as plugins
import pandas as pd
import vega
import firebase_admin
from firebase_admin import credentials, db
#from firebase import firebase


app = Flask(__name__)
compress = Compress(app)

'''
    @desc funcao de teste da aplicacao. Para acessar: http:IP/DNS:PORTA/app
'''
@app.route("/app")
def hello():
    user = os.getenv('TEST_VARIABLE') if 'TEST_VARIABLE' in os.environ else ' usuário rodando local!'
    return "Hi!" + user


'''
    @desc Rota principal do chat
    @params none
    @return retorna o html do chat
'''
@app.route('/chat')
def chat():
    return render_template('chat.html')


if __name__ == '__main__':
    if 'LOCAL_ENV' in os.environ:
        app.run(host='0.0.0.0', port=5000, debug=True)
    else:
        app.run(host='0.0.0.0', debug=True, port=os.environ.get('PORT'))
