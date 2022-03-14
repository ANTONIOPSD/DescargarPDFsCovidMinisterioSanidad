
# Script que descarga los PDFs de las actualizaciones de los casos de COVID-19 del ministerio de sanidad de España.
# El script escanea también todos los PDFs y busca la tabla de casos por franja de edad y las copia a una carpeta.
# El script extrae tambén las páginas donde están esas tablas y las une en un solo PDF.
# 
# Hecho a lo rápido, se podría optimizar todo. Podría dejar de funcionar en cualquier momento.
#
# Probado en Python 3.10.2
#
# Creado por https://t.me/gambinaceo




# Módulos necesarios
import os
import sys
import gc
import ctypes
import subprocess
import requests
from requests.structures import CaseInsensitiveDict
import shutil
import fitz # pip install PyMuPDF
import glob
import time  
from datetime import datetime
#import threading -> Para futura descarga en paralelo, actualmente va de uno en uno.


# Establece la carpeta de trabajo a la carpeta desde donde se ejecuta el script 
# y deshabilitar hacer click en la consola para evitar la pausa del script.
os.chdir(os.path.dirname(__file__))
kernel32 = ctypes.windll.kernel32
kernel32.SetConsoleMode(kernel32.GetStdHandle(-10), 128)

# CAMBIAR ESTO CONFORME SE NECESITE
numero_pdf_inicial = 1 # Número por el cual empezar a comprobar.
numero_pdf_final = 1000 # Número del PDF hasta el que se quiere llegar (aunque no exista todavía)
forzar_descarga = 0 # 0= Descargar solo entre las 7 de la mañana y las 10 de la noche | 1= Descargar sin esperar
carpeta_principal = 'PDFs Actualizaciones Coronavirus Ministerio de Sanidad'
carpeta_pdfs = 'PDFs'
carpeta_pdfs_casos = 'PDFs Con Gravedad Casos'
#####################################

# Creación de subcarpetas si no existen
if not os.path.exists(f'{carpeta_principal}'):
    os.makedirs(f'{carpeta_principal}')
if not os.path.exists(f'{carpeta_principal}/{carpeta_pdfs}'):
    os.makedirs(f'{carpeta_principal}/{carpeta_pdfs}')
if not os.path.exists(f'{carpeta_principal}/{carpeta_pdfs_casos}'):
    os.makedirs(f'{carpeta_principal}/{carpeta_pdfs_casos}')

listado_enlaces = [] # Creación de lista para usarla más adelante.

# Headers para request
headers = CaseInsensitiveDict()
headers["User-Agent"] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36"
headers["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
headers["Accept-Language"] = "es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3"
headers["Accept-Encoding"] = "gzip, deflate, br"
headers["Connection"] = "keep-alive"
headers["Upgrade-Insecure-Requests"] = "1"
headers["Sec-Fetch-Dest"] = "document"
headers["Sec-Fetch-Mode"] = "navigate"
headers["Sec-Fetch-Site"] = "none"
headers["Sec-Fetch-User"] = "?1"


# Funciones
def estado_pdf_en_web(numero): # Función para comprobar si el PDF existe sin tener que descargarlo.
    url = f'https://www.sanidad.gob.es/profesionales/saludPublica/ccayes/alertasActual/nCov/documentos/Actualizacion_{numero}_COVID-19.pdf'
    try:
        estado = requests.head(url, headers=headers, timeout=30).status_code
        return estado
    except:
        print(f'Error al comprobar la existencia el PDF {numero}.')
        esperar_tiempo(60)
        os.system('cls')
        gc.collect()
        subprocess.Popen(["python", f"DescargarPDFs.py"])
        sys.exit()

def descargar_pdf(numero): # Función para descargar el PDF sedún su número.
    url = f'https://www.sanidad.gob.es/profesionales/saludPublica/ccayes/alertasActual/nCov/documentos/Actualizacion_{numero}_COVID-19.pdf'
    try:
        archivo_pdf = requests.get(url, headers=headers, timeout=60)
        with open(f'{carpeta_principal}/{carpeta_pdfs}/Actualizacion_{numero}_COVID-19.pdf', 'wb') as pdf:
            pdf.write(archivo_pdf.content)
            print(f'PDF {numero}, descargado.')
    except:
        print(f'Error al descargar el PDF {numero}. Vuelve a ejecutar el script para intentar descargar los que falten')
        esperar_tiempo(60)
        os.system('cls')
        gc.collect()
        subprocess.Popen(["python", f"DescargarPDFs.py"])
        sys.exit()

def comprobar_tabla_casos(numero): # Función para escanear los PDF y comprobar si contiene la tabla de casos por gravedad.
    with fitz.open(f'{carpeta_principal}/{carpeta_pdfs}/Actualizacion_{numero}_COVID-19.pdf') as doc:
        for page in doc:
            texto_pagina = page.get_text()
            if 'Gravedad del caso' in texto_pagina: # Si el PDF contiene la tabla de casos, se copia a una carpeta para mantenerlos ordenador.
                original = f'{carpeta_principal}/{carpeta_pdfs}/Actualizacion_{numero}_COVID-19.pdf'
                destino = f'{carpeta_principal}/{carpeta_pdfs_casos}/Actualizacion_{numero}_COVID-19.pdf'
                shutil.copyfile(original, destino)
                break

def extraer_tablas_casos(): # Función para extraer la tabla de casos de todos los PDFs que la contiene.
    total_pdfs_casos_final = sorted(glob.glob(f'{carpeta_principal}/{carpeta_pdfs_casos}/Actualizacion*.pdf'), key=len)
    if total_pdfs_casos_final > total_pdfs_casos_inical: 
        print('Iniciando la creación del PDF con las tablas de casos por edad.')
        if os.path.exists(f'{carpeta_principal}/{carpeta_pdfs_casos}/_Tablas Extraídas Gravedad Casos.pdf'):
            os.remove(f'{carpeta_principal}/{carpeta_pdfs_casos}/_Tablas Extraídas Gravedad Casos.pdf')
        time.sleep(2)
        pdfs = sorted(glob.glob(f'{carpeta_principal}/{carpeta_pdfs_casos}/*.pdf'), key=len)
        ultima_pagina = 0
        doc2 = fitz.open()
        for id_pdf, pdf in enumerate(pdfs):
            with fitz.open(pdf) as doc:
                print(f'Leyendo {pdf}')
                for id_pagina, page in enumerate(doc):
                    text = page.get_text()
                    if 'Gravedad del caso*' in text:
                        print(f'Tabla10 encontrada en página {id_pagina} del PDF {id_pdf}')
                        doc2.insert_pdf(doc, from_page = id_pagina, to_page = id_pagina)
                        print(f'Página {id_pagina} insertada en página {ultima_pagina}')
                        ultima_pagina = ultima_pagina + 1
        doc2.save(f'{carpeta_principal}/{carpeta_pdfs_casos}/_Tablas Extraídas Gravedad Casos.pdf')
    else:
        print('No hay nuevos PDFs de casos, no se generará el PDF de casos.')

def esperar_tiempo(tiempo_espera): # Función para esperar x segundos y mostrar un mensaje con el tiempo.
    for segundo in range(1, tiempo_espera):
            if segundo == 1:
                print(f'Esperando {segundo} segundo de {tiempo_espera}')
            else:
                print(f'Esperando {segundo} segundos de {tiempo_espera}')
            time.sleep(1)

def comprobar_hora_inicio(): # Función para comprobar la hora  y descargar solo entre las 7 de la mañana y las 10 de la noche. 
    if forzar_descarga != 1:
        hora_actual = datetime.now().hour
        minuto_actual = datetime.now().minute
        hora_minutos = f'{hora_actual}:{minuto_actual}'
        while hora_actual < 7 or hora_actual > 21:
            print(f'Son las {hora_minutos}, el script empezará las descargas a las 7 de la mañana, cambia forzar_descarga a 1 para descargar a cualquier hora.')
            esperar_tiempo(300)
            hora_actual = datetime.now().hour
            minuto_actual = datetime.now().minute
            hora_minutos = f'{hora_actual}:{minuto_actual}'
            os.system('cls')
    return 1

def iniciar_procesos(numero):
    pdf_descargado = os.path.exists(f'{carpeta_principal}/{carpeta_pdfs}/Actualizacion_{numero}_COVID-19.pdf')
    pdf_casos_copiado = os.path.exists(f'{carpeta_principal}/{carpeta_pdfs_casos}/Actualizacion_{numero}_COVID-19.pdf')
    if (pdf_descargado is True and pdf_casos_copiado is True and numero < 511) or (pdf_descargado is True and pdf_casos_copiado is False and numero < 511):
        print(f'El PDF {numero} ya está descargado, pasado al siguiente.')
    elif pdf_descargado is True and pdf_casos_copiado is False:
        print(f'El PDF {numero} ya está descargado, comprobando casos y pasado al siguiente.')
        comprobar_tabla_casos(numero)
        
    if pdf_descargado is False:
        estado_web = estado_pdf_en_web(numero)
        if estado_web < 400:
            descargar_pdf(numero)
        if estado_web >= 400 and estado_web < 500:
            print(f'El PDF {numero} no existe en la web de ministerio de sanidad.')
        if estado_web >= 500:
            print(f'El servidor ha devuelto un error al intentar comprobar la existencia del PDF {numero}.')


def main(): # Función principal.
    comprobar_hora_inicio()
    global total_pdfs_inicial
    global total_pdfs_casos_inical
    total_pdfs_inicial = sorted(glob.glob(f'{carpeta_principal}/{carpeta_pdfs}/Actualizacion*.pdf'), key=len)
    total_pdfs_casos_inical = sorted(glob.glob(f'{carpeta_principal}/{carpeta_pdfs_casos}/Actualizacion*.pdf'), key=len)
    print('Iniciando descarga y análisis de los PDFs...')
    time.sleep(2)
    for numero in range(numero_pdf_inicial, numero_pdf_final):
        iniciar_procesos(numero)
        numero = numero + 1
    extraer_tablas_casos()

    # total_pdfs_final = sorted(glob.glob(f'{carpeta_principal}/{carpeta_pdfs}/*.pdf'), key=len)
    # if total_pdfs_final > total_pdfs_inicial: 
    #    pass # Check para futuro envío de mensajes

    print('Proceso completado, esperando unos segundos y empezando de nuevo')
    esperar_tiempo(60)
    os.system('cls')
    gc.collect()
    subprocess.Popen(["python", f"DescargarPDFs.py"])
    sys.exit()

if __name__ == "__main__":
    main()
