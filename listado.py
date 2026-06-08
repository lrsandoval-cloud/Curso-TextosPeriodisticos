from bs4 import BeautifulSoup
import os

# Colocar los nombres usados en los listados de resultados para cada medio
medios = ['elpais-es', 'elespectador', 'elpais-uy']

archivos_medio = []
archivos = os.listdir('listados')
archivos.sort()

for medio in medios:

    archivo_resultado = open('listados/' + medio + '.txt', 'w')
    archivo_resultado.close()
    archivo_resultado = open('listados/' + medio + '.txt', 'a')

    for archivo in archivos:
        if medio == archivo[:len(medio)] and archivo[-4:] == 'html':
            print(archivo)
            pagina = open('listados/' + archivo, 'r')

            sopa = BeautifulSoup(pagina, 'lxml')

            notas = sopa.find_all('h3')

            for nota in notas:
                print(nota.text)
                try:
                    enlace = nota.find_parent('a')['href']
                    archivo_resultado.write(enlace + '\n')
                    print(enlace)
                except KeyError:
                    print('Error KeyError')
                print()

    archivo_resultado.close()