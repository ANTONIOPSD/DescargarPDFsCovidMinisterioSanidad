# DescargarPDFsCovidMinisterioSanidad
Script para descargar los PDFs de los casos COVID del Ministerio de Sanidad de España.

Script que descarga los PDFs de las actualizaciones de los casos de COVID-19 del ministerio de sanidad de España.
El script escanea también todos los PDFs y busca la tabla de casos por franja de edad y las copia a una carpeta.
El script extrae tambén las páginas donde están esas tablas y las une en un solo PDF.

Hecho a lo rápido, se podría optimizar todo. Podría dejar de funcionar en cualquier momento.
Probado en Python 3.10.2
Creado por https://t.me/gambinaceo

Módulos necesarios:

os
sys
gc
ctypes
subproces
requests
shutil
PyMuPDF
glob
time
datetime
