sitio = 'elpais.com.uy'

keywords = ['adolescencia,adolescentes', 'tecnologia']
cantidad = 50 # cantidad de resultados por período
fecha_inicial = '2026-04-01' # Tener en cuenta que el período arranca un día después de esta fecha
fecha_final = '2026-05-30'
periodo = 30 # en días

from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from subprocess import getoutput
import time
import platform

fecha_arranque = datetime.strptime(fecha_inicial, '%Y-%m-%d').date()
fecha_limite = datetime.strptime(fecha_final, '%Y-%m-%d').date()
paso = timedelta(days=periodo)
un_dia = timedelta(days=1)

palabra = ''
for keyw in keywords:
    if len(keyw.split(",")) > 1:
        palabra += '(' + keyw.replace(',','+OR+') + ')+AND+'
    else:
        palabra += keyw + '+AND+'
palabra = palabra[:-5]


options = Options()
sistema_actual = platform.system()
if sistema_actual == "Linux":
    options.binary_location = getoutput("find /snap/firefox -name firefox").split("\n")[-1]
    driver = webdriver.Firefox(
        service=Service(executable_path=getoutput("find /snap/firefox -name geckodriver").split("\n")[-1]),
        options=options)
elif sistema_actual == "Windows":
    driver = webdriver.Firefox(options=options)


while fecha_arranque <= fecha_limite:
    consulta = 'https://www.google.com.ar/search?q=' + palabra + '+site%3A' + sitio
    consulta += '+after%3A' + str(fecha_arranque)
    consulta += '+before%3A' + str(fecha_arranque + paso)
    consulta += '&start='
    fecha_arranque = fecha_arranque + paso + un_dia

    for i in range(0, cantidad, 10):
        url = consulta + str(i)
        #print(url)

        driver.get(url)

        if i < 10:
            paginado = '00' + str(i)
            time.sleep(40)
        elif i >= 10 and i < 100:
            paginado = '0' + str(i)
            time.sleep(5)
        else:
            paginado = str(i)
            time.sleep(5)

        h3s = driver.find_elements(By.TAG_NAME, "h3")
        if not h3s:
            break
        else:
            html = driver.page_source
            with open('listados/' + sitio + '_' + str(fecha_arranque) + '_' +  paginado + '.html', "w", encoding="utf-8") as f:
                f.write(html)


driver.quit()