import dropbox
import os

# Recuperar token de la variable de entorno
dropbox_token = os.getenv('DROPBOX_TOKEN')
if not dropbox_token:
    raise Exception("El token de Dropbox no está configurado como variable de entorno.")

# Conectar con Dropbox
dbx = dropbox.Dropbox(dropbox_token)

# Listar archivos en la carpeta raíz
try:
    result = dbx.files_list_folder("")
    print("Archivos disponibles:")
    for entry in result.entries:
        print(f"- {entry.name}")
except dropbox.exceptions.AuthError as e:
    print(f"Error de autenticación: {e}")
