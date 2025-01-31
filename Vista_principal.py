from flask import Flask, render_template, request, redirect, url_for
from dropbox import Dropbox

# Configuración de la aplicación Flask
app = Flask(__name__)

dropbox_token = None  # Variable global para almacenar el token de Dropbox

# Ruta para la pantalla de bienvenida
@app.route('/', methods=['GET', 'POST'])
def welcome():
    global dropbox_token
    if request.method == 'POST':
        dropbox_token = request.form.get('dropbox_token')
        if dropbox_token:
            return redirect(url_for('main_menu'))
    return render_template('welcome.html')

# Ruta para la pantalla principal
@app.route('/main', methods=['GET', 'POST'])
def main_menu():
    if not dropbox_token:
        return redirect(url_for('welcome'))

    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'constancia':
            return redirect(url_for('constancia'))
        elif action == 'opinion':
            return redirect(url_for('opinion'))

    return render_template('main_menu.html')

# Ruta para la funcionalidad de Constancias de Situación Fiscal
@app.route('/constancia')
def constancia():
    return "Funcionalidad para Constancias de Situación Fiscal en desarrollo."

# Ruta para la funcionalidad de Opinión del Cumplimiento
@app.route('/opinion')
def opinion():
    return "Funcionalidad para Opinión del Cumplimiento en desarrollo."

if __name__ == '__main__':
    app.run(debug=True)
