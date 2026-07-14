idioma = 'es' # Opciones: es (español), en (inglés)

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import NMF
from funciones import obtener_stop_words

cantidad_temas = 8    # Cantidad aproximada de temas en que agrupará los artículos
                       # colocar "auto" si se quiere que el algoritmo lo estime


base = pd.read_pickle('pickles/base.pkl')

# 1. Vectorización con TF-IDF
# Usamos max_df/min_df para filtrar palabras demasiado comunes o demasiado raras
tfidf_vectorizer = TfidfVectorizer(
    max_df=0.95,          # Ignora palabras que aparecen en más del 95% de los artículos
    min_df=2,             # Ignora palabras que aparecen en menos de 2 artículos
    stop_words=obtener_stop_words(idioma)  # Filtro básico de stopwords (por si quedó alguna)
)

tfidf_matrix = tfidf_vectorizer.fit_transform(base['lemas'])

# 2. Configurar y entrenar NMF
# Definimos un número estimado de temas (ej. 10) para empezar la exploración
n_topics = cantidad_temas
nmf_model = NMF(
    n_components=n_topics,
    random_state=42,
    init='nndsvd'          # Inicialización ideal para datos dispersos como texto
)

nmf_model.fit(tfidf_matrix)

def mostrar_temas(model, vectorizer, n_top_words):
    keywords = []
    words = vectorizer.get_feature_names_out()
    for topic_idx, topic in enumerate(model.components_):
        # Tomamos los índices de las palabras con mayor peso en el tema
        top_words_idx = topic.argsort()[:-n_top_words - 1:-1]
        top_words = [words[i] for i in top_words_idx]
        keywords.append(", ".join(top_words))
    return keywords

# Mostramos las 10 palabras más importantes de cada uno de los 10 temas
keywords = mostrar_temas(nmf_model, tfidf_vectorizer, 10)

# Obtenemos la matriz Documento-Tema
w_matrix = nmf_model.transform(tfidf_matrix)

# Encontramos el índice del tema con mayor peso para cada fila
base['tema_principal'] = w_matrix.argmax(axis=1)
# Guardamos también el grado de confianza o peso de ese tema
base['score_tema'] = w_matrix.max(axis=1)

# Iteramos sobre cada tema ordenado para mostrar sus mejores representantes
for tema_id in sorted(base['tema_principal'].unique()):
    print(f"TEMA #{tema_id}")

    # Filtramos el DataFrame para el tema actual
    df_tema = base[base['tema_principal'] == tema_id]

    # Ordenamos por score de mayor a menor y tomamos los 5 mejores
    top_articulos = df_tema.sort_values(by='score_tema', ascending=False).head(5)
    print(keywords[tema_id])
    print()
    # Imprimimos los resultados
    for idx, fila in top_articulos.iterrows():
        # Redondeamos el score a 4 decimales para que quede más prolijo
        score = round(fila['score_tema'], 4)
        print(f"[Score: {score}] - {fila['titulo']}")

        # Opcional: Descomenta la línea de abajo si querés ver también el copete
        # print(f"   ↳ Copete: {fila['copete']}\n")

    print("=" * 50)


import seaborn as sns
import matplotlib.pyplot as plt

# Creamos un dataframe con la matriz documento-tema
df_pesos_temas = pd.DataFrame(w_matrix, columns=[f"Tema #{i}" for i in range(cantidad_temas)])

# Calculamos la correlación de Pearson entre las columnas (temas)
matriz_correlacion = df_pesos_temas.corr()

# Graficamos un mapa de calor (Heatmap)
plt.figure(figsize=(10, 8))
sns.heatmap(matriz_correlacion, annot=True, cmap='coolwarm', fmt=".2f")
plt.title("Transversalidad: ¿Qué temas suelen aparecer juntos en las mismas notas?")
plt.show()