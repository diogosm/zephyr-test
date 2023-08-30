from flask import Flask, request, jsonify, render_template, url_for, session
from flask_compress import Compress
from functools import wraps
import os
import secrets
import datetime
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
import openai
#import torch
import transformers
import wandb
import numpy as np
from tqdm import tqdm

app = Flask(__name__)
app.config["SECRET_KEY"] = "supersecretkey"
compress = Compress(app)

openai.api_key = os.getenv('OPENAI_API_KEY')

class User:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.messages = []

    def addMsg(self, msg):
        self.messages.append(msg)

    def getMsgs(self):
        return self.messages

'''
    FUNCOES GPT
'''
'''
  Valores possíveis: openai.Model.list()
    "gpt-3.5-turbo"
    "gpt-4"
'''
MODEL_GPT = "gpt-3.5-turbo"

def promptSystemMain():
    prompt=f"""
    Você irá atuar como um assistente para construção de currículo de um usuário para conseguir emprego.
    Seu nome é Zephyr.
    Você irá perguntar os seguintes dados pessoais: nome, idade e experiência profissional, habilidade e desafios enfrentados e resolvidos nos empregos anteriores.
    Comece perguntando nome e idade, e após a resposta, pergunte a quantidade de empregos anteriores como experiência profissional.
    Pergunte também as habilidades que ele julga ter mais competência.
    Pergunte os maiores desafios que ele enfrentou e resolveu em cada emprego.
    Evite fazer perguntas já feitas previamente, com exceção daquelas ainda não respondidas e evite ser repetitivo no modo de falar.
    Evite ser repetitivo.
    Para cada dado de experiência profissional, você irá sugerir perguntas que se relacionem com essa experiência como:
      tempo de trabalho, quantidade de experiências para cada emprego anterior e suas funções em cada um destes empregos. Pergunte isso para cada emprego citado.
    Após ter todos esses dados, finalize com a resposta 'Já tenho todos os dados necessários para finalizar, obrigado.'.
    Se um assunto fugir da temática assistência em construção de currículo, responda 'Desculpa, não reconheço esse tipo de informação ou questionamento.'.
  """
    return {"role": "system", "content": prompt}


def promptOutputCurriculum():
    prompt=f"""
    Gere o conteúdo abaixo como se fosse a própria pessoa falando de si mesmo, as suas características e seu resumo. Utilize o pronome eu quando necessário.
    Gere o resumo da conversa com padrão de bullets como formato de saída:
    - Características da pessoa
      - Nome: detalhes
      - Idade: detalhes
    - Características pessoais
      - Experiência profissional: crie um resumo de até 2 parágrafos
      - Tempo de experiência: crie um resumo em 1 parágrafo e some o total de tempo de experiência
    - Resumo
      - Gere um resumo de 1 ou 2 parágrafos falando das qualidades e aptidões da pessoa, além de suas habilidades.
  """
    return {"role": "user", "content": prompt}


def in_chat(system_msg, user_msg, user_assistant):
    assert isinstance(system_msg, str), "`system_msg` precisa ser uma string"
    assert isinstance(user_msg, str), "`user_msg` precisa ser uma string"
    assert isinstance(user_assistant, str), "`user_assistant` precisa ser uma string"


def tryChat(question):
    assert isinstance(question, str), "`question` precisa ser uma string"
    ## verificar alguma restricao da questao
    return True


'''
  funcao que envia um http request pro gpt e retorna o json de resposta.
  Doc principal: https://platform.openai.com/docs/api-reference/chat/create?lang=python
  @TODO
    try/catch para verificar se a api retornou erro ou triggerizar excecao
'''
def sendItToGPT(role, msgs):
    global MODEL_GPT
    assert isinstance(msgs, list), '`msgs` precisa ser um list'

    response = openai.ChatCompletion.create(
        model=MODEL_GPT,
        messages=msgs,
        temperature=0.65,         ## flag de criatividade do bot
        presence_penalty=0.8,     ## flag para evitar ser repetitivo, quanto maior, mais diversificado
        frequency_penalty=0.7,    ## outra flag para evitar ser repetitivo
        n=1,
        stop=None
    )
    return response


'''
  funcao para treinaer modelo no fine tuning
  @TODO
    tudo
'''
def treinaModelo():
    return True

exitWords = ['fim', 'obrigado', 'sair']
'''
    FIM FUNCOES GPT
'''


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
    session_id = secrets.token_hex(16)
    print(session_id, flush=True)
    createSession(session_id)
    print(getSession(session_id), flush=True)
    print('API: ', openai.api_key, flush=True)
    print('API: ', os.getenv('OPENAI_API_KEY'), flush=True)
    return render_template('chat.html', session_id=session_id)


@app.route('/newMessage', methods=['POST'])
def newMessage():
    session_id = request.form.get('session_id')
    message = request.form.get('message')

    user = getSession(session_id)
    print('USER: ', user, flush=True)
    ans = handle(user, message)
    print('SESSION ', session, flush=True)

    # Process the session_id and message as needed
    # return "New message received from session_id: {} - Message: {}".format(session_id, message)
    return ans


def handle(user, message):
    if len(user['messages']) == 0:
        user['messages'].append(promptSystemMain())
        user['messages'].append({"role": "user", "content": "Se apresente com um certo grau de " +
                                                         "informalidade e intimidade com seu nome e sua função em poucas palavras e peça para eu me apresentar com meu nome completo e idade."})
        ans = sendItToGPT('', user['messages'])
        print(ans['choices'][0]['message']['content'], flush=True)
        session[user['id']] = user
        return ans['choices'][0]['message']['content']
    else:
        user['messages'].append({"role": "user", "content": message})
        # print(user.getMsgs(), flush=True)
        ans = sendItToGPT('', user['messages'])

        formatted_ans = json.dumps(ans, indent=4)
        # print(formatted_ans)
        print('Zephyr: ' + ans['choices'][0]['message']['content'], flush=True)
        ## add resposta do assistente para o fluxo
        user['messages'].append({"role": "assistant",
                     "content": ans['choices'][0]['message']['content']})
        session[user['id']] = user
        return ans['choices'][0]['message']['content']


def createSession(session_id):
    user = User(session_id, '')
    user.timestamp = datetime.datetime.now()
    session[session_id] = user.__dict__


def getSession(session_id):
    user = session.get(session_id)
    return user


if __name__ == '__main__':
    if 'LOCAL_ENV' in os.environ:
        app.run(host='0.0.0.0', port=5000, debug=True)
    else:
        app.run(host='0.0.0.0', debug=True, port=os.environ.get('PORT'))
