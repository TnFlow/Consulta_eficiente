from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dropbox import Dropbox
import time

# Función para extraer RFCs y contraseñas desde un archivo de Dropbox
def get_user_credentials(dropbox_token, file_path):
    dbx = Dropbox(dropbox_token)
    _, res = dbx.files_download(file_path)
    content = res.content.decode('utf-8')
    credentials = []
    for line in content.splitlines():
        rfc, password = line.split(',')
        credentials.append((rfc.strip(), password.strip()))
    return credentials

# Función principal para interactuar con el portal SAT
def process_users(dropbox_token, file_path):
    # Configuración del WebDriver
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Ejecutar en modo headless si no necesitas ver el navegador
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(options=options)

    try:
        # URL del portal del SAT
        url = "https://www.sat.gob.mx"
        driver.get(url)

        # Esperar a que cargue la página principal
        wait = WebDriverWait(driver, 10)
        otros_tramites = wait.until(EC.presence_of_element_located((By.LINK_TEXT, "Otros trámites y servicios")))
        otros_tramites.click()

        # Navegar al apartado de "Genera tu Constancia de Situación Fiscal"
        constancia_fiscal = wait.until(EC.presence_of_element_located((By.LINK_TEXT, "Genera tu Constancia de Situación Fiscal")))
        constancia_fiscal.click()

        # Obtener las credenciales desde Dropbox
        credentials = get_user_credentials(dropbox_token, file_path)

        # Procesar cada usuario
        for rfc, password in credentials:
            # Localizar e ingresar RFC
            rfc_input = wait.until(EC.presence_of_element_located((By.ID, "rfc")))
            rfc_input.clear()
            rfc_input.send_keys(rfc)

            # Localizar e ingresar contraseña
            password_input = wait.until(EC.presence_of_element_located((By.ID, "password")))
            password_input.clear()
            password_input.send_keys(password)

            # Simular el inicio de sesión
            login_button = wait.until(EC.element_to_be_clickable((By.ID, "login-button")))
            login_button.click()

            # Esperar la generación de la constancia
            time.sleep(5)  # Ajusta este tiempo según sea necesario

            # Descargar o verificar la constancia
            # Aquí puedes agregar lógica para guardar la constancia o verificar su estado

            print(f"Procesado usuario con RFC: {rfc}")

            # Cerrar sesión antes de continuar con el siguiente usuario
            logout_button = wait.until(EC.element_to_be_clickable((By.ID, "logout-button")))
            logout_button.click()

    except Exception as e:
        print(f"Error: {e}")

    finally:
        driver.quit()

# Parámetros para el programa
dropbox_token = "TU_ACCESS_TOKEN_DE_DROPBOX"
file_path = "/ruta/al/archivo/credenciales.txt"

# Ejecutar el programa
process_users(dropbox_token, file_path)
