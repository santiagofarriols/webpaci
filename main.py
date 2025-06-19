from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import os

app = Flask(__name__)

@app.route('/get-events', methods=['POST'])
def get_events():
    # Seguridad con API Key
    api_key = request.headers.get('X-API-KEY')
    if api_key != os.environ.get('API_KEY'):
        return jsonify({'error': 'Unauthorized'}), 401

    # Datos del usuario
    data = request.get_json()
    user = data['username']
    pwd = data['password']

    # URLS primero
    login_url = 'https://haz-prod-webapp.azurewebsites.net/gamexamplelogin.aspx'
    agenda_url = 'https://haz-prod-webapp.azurewebsites.net/agenda.aspx'

    # Headers con Referer correcto
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": login_url
    }

    session = requests.Session()

    # Paso 1: obtener tokens de la página de login
    login_page = session.get(login_url, headers=headers)
    soup = BeautifulSoup(login_page.text, 'html.parser')

    viewstate_tag = soup.find(id='__VIEWSTATE')
    eventvalidation_tag = soup.find(id='__EVENTVALIDATION')

    if not viewstate_tag or not eventvalidation_tag:
        print("❌ No se encontró __VIEWSTATE o __EVENTVALIDATION")
        print("Login HTML (parcial):", login_page.text[:500])
        return jsonify({'error': 'Login page did not return expected tokens'}), 500

    viewstate = viewstate_tag['value']
    eventvalidation = eventvalidation_tag['value']

    # Paso 2: enviar login
    payload = {
        '__VIEWSTATE': viewstate,
        '__EVENTVALIDATION': eventvalidation,
        'txtUsername': user,
        'txtPassword': pwd,
        'btnLogin': 'Entrar',
    }

    response = session.post(login_url, data=payload, headers=headers, allow_redirects=True)
    print("✅ POST Login status:", response.status_code)
    print("📝 Login preview:", response.text[:300])

    # Paso 3: acceder a la agenda
    agenda_page = session.get(agenda_url, headers=headers)
    soup = BeautifulSoup(agenda_page.text, 'html.parser')

    # Extraer eventos (ajustá la clase real si es necesario)
    eventos = []
    for e in soup.find_all('div', class_='nombre-clase-evento'):
        eventos.append(e.text.strip())

    return jsonify({'eventos': eventos})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
