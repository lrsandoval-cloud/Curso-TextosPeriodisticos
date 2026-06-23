import pandas as pd

base = pd.read_pickle('pickles/base.pkl')

rotulos = list(base['medio'].unique())

sentimientos = pd.read_pickle('pickles/sentimientos.pkl')
sentimientos['label'] = sentimientos['label'].astype(int)


from statistics import mean
from statistics import median
from statistics import mode

print ('-------------- DATOS GENERALES')
print('Media de label:', mean(sentimientos['label']))
print('Mediana de label:', median(sentimientos['label']))
print('Moda de label:', mode(sentimientos['label']))
print('Media de score:', mean(sentimientos['score']))
print('Score mínimo:', sentimientos.iloc[sentimientos['score'].idxmin(), 2])
print('Score máximo:', sentimientos.iloc[sentimientos['score'].idxmax(), 2])

scores = [0, 0.5, 0.6, 0.8] # Modificar estos valores si se quiere que la tabla indique valores de
                            # corte distintos
tabla = []
for sc in scores:
    linea = []
    menos_sentimientos = sentimientos[sentimientos['score'] > sc].copy()
    linea.append(sc)
    linea.append(len(menos_sentimientos))
    linea.append(mean(menos_sentimientos['label']))
    linea.append(median(menos_sentimientos['label']))
    linea.append(mode(menos_sentimientos['label']))
    linea.append(mean(menos_sentimientos['score']))
    tabla.append(linea)

confiabilidades = pd.DataFrame(tabla, columns=['score_menor_a', 'N', 'media', 'mediana', 'moda', 'media_score'])

print("\n----------- Valores medios de acuerdo a rangos de confiabilidad")
print(confiabilidades.to_string(index=False))

score_minimo = 0.5 # Modificar este valor si se quiere indicar otro valor de corte

sentimientos_minimo = sentimientos[sentimientos['score'] > score_minimo].copy()
rotulos = list(sentimientos['medio'].unique())
resultado = []
for medio in rotulos:
    fila = [medio]
    sentimientos_medio = sentimientos_minimo[sentimientos_minimo['medio']==medio].copy()
    fila.append(mean(sentimientos_medio['label']))
    fila.append(median(sentimientos_medio['label']))
    fila.append(mode(sentimientos_medio['label']))
    fila.append(mean(sentimientos_medio['score']))
    resultado.append(fila)
    fila = []

fila = ['Todos']
fila.append(mean(sentimientos_medio['label']))
fila.append(median(sentimientos_medio['label']))
fila.append(mode(sentimientos_medio['label']))
fila.append(mean(sentimientos_medio['score']))
resultado.append(fila)

df_resultado = pd.DataFrame(resultado, columns=['medio', 'media de label', 'mediana de label', 'moda de label', 'media de score'])
print()
print("\n----------- Valores medios según medio (score > " + str(score_minimo) + ")")
print(df_resultado.to_string(index=False))

#exit()


sentimientos['fecha'] = pd.to_datetime(sentimientos['fecha'])
sentimientos['mes'] = sentimientos['fecha'].dt.to_period('M')   # formato YYYY-MM
promedios = sentimientos.groupby('mes')['label'].mean().reset_index()

import matplotlib.pyplot as plt

plt.plot(promedios['mes'].astype(str), promedios['label'], marker='o')
plt.xticks(rotation=45)
plt.xlabel('Mes')
plt.ylabel('Promedio')
plt.title('Promedio mensual de sentimiento')
plt.tight_layout()
plt.show()


#exit()

prom = sentimientos.groupby(['mes', 'medio'])['label'].mean().reset_index()
pivot = prom.pivot(index='mes', columns='medio', values='label')

plt.figure(figsize=(10,6))

for medio in pivot.columns:
    plt.plot(pivot.index.astype(str), pivot[medio], marker='o', label=medio)

plt.xlabel('Mes')
plt.ylabel('Promedio de sentimiento')
plt.title('Sentimiento promedio mensual por medio')
plt.xticks(rotation=45)
plt.legend(title='Medio')
plt.tight_layout()
plt.show()



base['label'] = 0.0
base['score'] = 0.0
for i, row in base.iterrows():
    segmento = sentimientos.query("idnota == " + str(i)).copy()
    if len(segmento) > 0:
        base.loc[i, 'label'] = mean(segmento['label'])
        base.loc[i, 'score'] = mean(segmento['score'])

base.to_pickle('pickles/base.pkl')


