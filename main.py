from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import os

app = Flask(__name__)

@app.route('/get-events', methods=['POST'])
def get_events():
    # Seguridad por API Key
    api_key = request.headers.get('X-API-KEY')
    if api_key != os.environ.get('API_KEY'):
        return jsonify({'error': 'Unauthorized'}), 401

    # Datos del usuario
    data = request.get_json()
    user = data['username']
    pwd = data['password']

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": login_url
    }

    session = requests.Session()

    login_url = 'https://haz-prod-webapp.azurewebsites.net/gamexamplelogin.aspx'
    agenda_url = 'https://haz-prod-webapp.azurewebsites.net/agenda.aspx'

    login_page = session.get(login_url, headers=headers)
    soup = BeautifulSoup(login_page.text, 'html.parser')

    viewstate_tag = soup.find(id='__VIEWSTATE')
    eventvalidation_tag = soup.find(id='__EVENTVALIDATION')

    if not viewstate_tag or not eventvalidation_tag:
        print("Error: No se encontró __VIEWSTATE o __EVENTVALIDATION")
        return jsonify({'error': 'Login page did not return expected tokens'}), 500

    viewstate = viewstate_tag['value']
    eventvalidation = eventvalidation_tag['value']

    payload = {
        '__VIEWSTATE': viewstate,
        '__EVENTVALIDATION': eventvalidation,
        'txtUsername': user,
        'txtPassword': pwd,
        'btnLogin': 'Entrar',
    }

    response = session.post(login_url, data=payload, headers=headers, allow_redirects=True)
    print("Login POST status:", response.status_code)
    print("Login POST response preview:", response.text[:300])

    agenda_page = session.get(agenda_url, headers=headers)
    soup = BeautifulSoup(agenda_page.text, 'html.parser')
    print("Status de login page:", login_page.status_code)
    print("Contenido login page (primeras líneas):")
    print(login_page.text[:500])

    eventos = []
    for e in soup.find_all('div', class_='nombre-clase-evento'):  # ajustar si necesario
        eventos.append(e.text.strip())

    return jsonify({'eventos': eventos})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
