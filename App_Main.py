from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import dropbox
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Cambia esta clave para producción

# Configuración de Dropbox API
dropbox_token = os.getenv('DROPBOX_TOKEN')  # Asegúrate de configurar esta variable de entorno con tu token de Dropbox
dbx = dropbox.Dropbox(dropbox_token)

# Configuración de Selenium
def setup_selenium():
    chrome_options = Options()
    chrome_options.add_argument('--incognito')
    chrome_options.add_argument('--headless')  # Opcional: Ejecutar en segundo plano
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    return driver

# Ruta para el menú principal
@app.route('/', methods=['GET', 'POST'])
def main_menu():
    if request.method == 'POST':
        client_name = request.form.get('client_name')
        if client_name:
            session['client_name'] = client_name  # Guardar el cliente seleccionado en la sesión
        return redirect(url_for('main_menu'))

    client_name = session.get('client_name', None)  # Obtener cliente de la sesión
    return render_template('main_menu_v2.html', client_name=client_name)

# Selección de cliente
@app.route('/select_client', methods=['POST'])
def select_client():
    client_name = request.form.get('client_name')
    if client_name:
        session['client_name'] = client_name  # Guardar cliente en sesión
    return redirect(url_for('main_menu'))  # Redirigir al menú principal


# Ruta para manejar las acciones de trámites
@app.route('/main', methods=['POST'])
def handle_action():
    action = request.form.get('action')
    client_name = session.get('client_name', None)

    if not client_name:
        return redirect(url_for('main_menu'))  # Redirigir si no hay cliente seleccionado

    try:
        # Intentar acceder a la carpeta del cliente en Dropbox
        folder_path = f"/01 CONTABILIDADES/PERSONAS FISICAS/CLIENTES VIGENTES{client_name}"
        result = dbx.files_list_folder(folder_path)

        # Buscar el único archivo .txt en la carpeta
        txt_files = [entry for entry in result.entries if isinstance(entry, dropbox.files.FileMetadata) and entry.name.endswith('.txt')]
        if len(txt_files) != 1:
            return f"Error: La carpeta debe contener exactamente un archivo .txt."

        # Descargar y procesar el archivo .txt
        metadata, response = dbx.files_download(txt_files[0].path_lower)
        content = response.content.decode('utf-8')

        # Extraer RFC y CIEC
        rfc, ciec = None, None
        for line in content.splitlines():
            if line.startswith('RFC:'):
                rfc = line.replace('RFC:', '').strip()
            elif line.startswith('CIEC:'):
                ciec = line.replace('CIEC:', '').strip()

        if not rfc or not ciec:
            return "Error: El archivo no contiene RFC o CIEC válidos."

        # Configurar Selenium
        driver = setup_selenium()

        # Abrir el portal del SAT
        driver.get('https://www.sat.gob.mx/')
        time.sleep(3)  # Esperar a que cargue la página principal

        # Navegar al apartado según la acción
        if action == 'constancia':
            driver.find_element(By.LINK_TEXT, 'Otros trámites y servicios').click()
            time.sleep(2)
            driver.find_element(By.LINK_TEXT, 'Genera tu Constancia de Situación Fiscal').click()
        elif action == 'opinion':
            driver.find_element(By.LINK_TEXT, 'Otros trámites y servicios').click()
            time.sleep(2)
            driver.find_element(By.LINK_TEXT, 'Opinión del Cumplimiento de Obligaciones Fiscales').click()
        else:
            driver.quit()
            return redirect(url_for('main_menu'))

        time.sleep(3)  # Esperar a que cargue la página del trámite

        # Ingresar RFC y CIEC
        driver.find_element(By.ID, 'rfc').send_keys(rfc)
        driver.find_element(By.ID, 'password').send_keys(ciec)
        driver.find_element(By.ID, 'password').send_keys(Keys.RETURN)

        time.sleep(5)  # Esperar a que se complete la autenticación
        driver.quit()

        return f"Consulta realizada para {client_name}. RFC: {rfc}"

    except dropbox.exceptions.ApiError as e:
        return f"Error al acceder a la carpeta de {client_name} en Dropbox: {e}"
    except Exception as e:
        return f"Error en la consulta con Selenium: {e}"

# Ruta para autocompletado del buscador
@app.route('/autocomplete', methods=['GET'])
def autocomplete():
    query = request.args.get('query', '').lower()
    suggestions = []

    try:
        # Listar todas las carpetas en la raíz de Dropbox
        result = dbx.files_list_folder("/01 CONTABILIDADES/PERSONAS FISICAS/CLIENTES VIGENTES")
        for entry in result.entries:
            if isinstance(entry, dropbox.files.FolderMetadata) and query in entry.name.lower():
                suggestions.append(entry.name)
    except dropbox.exceptions.ApiError as e:
        return jsonify({"error": f"Error al obtener las carpetas: {e}"})

    return jsonify(suggestions)

if __name__ == '__main__':
    app.run(debug=True)
