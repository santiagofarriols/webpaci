from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import os

app = Flask(__name__)

@app.route('/get-events', methods=['POST'])
def get_events():
    user = request.json['username']
    pwd = request.json['password']

    session = requests.Session()
    login_url = 'https://haz-prod-webapp.azurewebsites.net/login.aspx'
    agenda_url = 'https://haz-prod-webapp.azurewebsites.net/agenda.aspx'

    login_page = session.get(login_url)
    soup = BeautifulSoup(login_page.text, 'html.parser')

    viewstate = soup.find(id='__VIEWSTATE')['value']
    eventvalidation = soup.find(id='__EVENTVALIDATION')['value']

    payload = {
        '__VIEWSTATE': viewstate,
        '__EVENTVALIDATION': eventvalidation,
        'txtUsername': user,
        'txtPassword': pwd,
        'btnLogin': 'Entrar',
    }

    session.post(login_url, data=payload)
    agenda_page = session.get(agenda_url)
    soup = BeautifulSoup(agenda_page.text, 'html.parser')

    eventos = []
    for e in soup.find_all('div', class_='nombre-clase-evento'):  # ajustar clase real
        eventos.append(e.text.strip())

    return jsonify({'eventos': eventos})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
