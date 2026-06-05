import pandas as pd

# Colocar aquí los nombres de los sitios
pickles = [ 'elpais-uy', 'lavanguardia', 'lanacion', 'elespectador']

base = pd.read_pickle('pickles/' + pickles[0] + '.pkl').copy()
base.drop(base.index, inplace=True)

for pick in pickles:
    pickle = pd.read_pickle('pickles/' + pick + '.pkl')
    base = pd.concat([base, pickle], ignore_index=True)


pd.to_pickle(base, 'pickles/base.pkl')

texto = '<!DOCTYPE html>\n<html lang="es">\n<head>\n<meta charset="UTF-8">\n</head>\n<body>\n'

for i, row in base.iterrows():
    cadena = ''
    try:
        cadena = '<p>[' + str(i) + '] <a href="' + row['url'] + '" target="blank_">' + row['titulo'] + '</a> [' + row['medio'] + ']</p>\n'
    except TypeError:
        cadena = '<p>[' + str(i) + ']</p>'
    texto += cadena

texto += '</body>\n</html>'

listado = open('listado.html', 'w')
listado.write(texto)
listado.close()