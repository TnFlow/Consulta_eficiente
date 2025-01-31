from flask import Flask, render_template, request, redirect, url_for, session
import dropbox
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Cambia esta clave para producción

# Configuración de Dropbox API
dropbox_token = os.getenv('DROPBOX_TOKEN')  # Asegúrate de configurar esta variable de entorno con tu token de Dropbox
dbx = dropbox.Dropbox(dropbox_token)

# Ruta para el menú principal
@app.route('/', methods=['GET', 'POST'])
def main_menu():
    if request.method == 'POST':
        client_name = request.form.get('client_name')
        if client_name:
            session['client_name'] = client_name  # Guardar el cliente seleccionado en la sesión
        return redirect(url_for('main_menu'))

    client_name = session.get('client_name', None)  # Obtener cliente de la sesión
    return render_template('Main_Menu.html', client_name=client_name)

# Ruta para manejar las acciones de trámites
@app.route('/main', methods=['POST'])
def handle_action():
    action = request.form.get('action')
    client_name = session.get('client_name', None)

    if not client_name:
        return redirect(url_for('main_menu'))  # Redirigir si no hay cliente seleccionado

    try:
        # Intentar acceder al archivo del cliente en Dropbox
        file_path = f"/{client_name}.txt"
        metadata, response = dbx.files_download(file_path)
        content = response.content.decode('utf-8')

        # Extraer RFC y contraseña del archivo (asumiendo formato RFC:contraseña en cada línea)
        credentials = content.strip().split("\n")
        rfc, password = credentials[0].split(":") if credentials else (None, None)

        if action == 'constancia':
            return f"Consultando constancia de {client_name}. RFC: {rfc}, Contraseña: {password}"
        elif action == 'opinion':
            return f"Consultando opinión de {client_name}. RFC: {rfc}, Contraseña: {password}"
        else:
            return redirect(url_for('main_menu'))
    except dropbox.exceptions.ApiError as e:
        return f"Error al acceder al archivo de {client_name} en Dropbox: {e}"
    except Exception as ex:
        return f"Error procesando el archivo de {client_name}: {ex}"

# Ruta para seleccionar cliente
@app.route('/select_client', methods=['POST'])
def select_client():
    client_name = request.form.get('client_name')
    if client_name:
        session['client_name'] = client_name  # Guardar el cliente seleccionado en la sesión
    return redirect(url_for('main_menu'))


@app.route('/constancia')
def constancia():
    return "Funcionalidad para Constancias de Situación Fiscal en desarrollo."

@app.route('/opinion')
def opinion():
    return "Funcionalidad para Opinión del Cumplimiento en desarrollo."

if __name__ == '__main__':
    app.run(debug=True)
