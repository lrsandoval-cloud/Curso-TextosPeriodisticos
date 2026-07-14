import pickle
import pandas as pd

cantidad_keywords = 15  # Cuántas palabras clave mostrará para cada tema
cantidad_articulos = 5  # y cuántos artículos (entre los más emblemáticos)
mostrar_articulos = True


pd.set_option('display.max_columns', None)
pd.set_option('display.width', 300)
pd.set_option('display.max_colwidth', 40)

base = pd.read_pickle('pickles/base_eng.pkl')

base['texto_completo'] = (
    base['titulo'].fillna('') + " " +
    base['copete'].fillna('') + " " +
    base['texto'].fillna('')
)

# 1. Cargado del pickle
with open('pickles/modelo_bertopic.pkl', 'rb') as f:
    topic_model = pickle.load(f)

# 2. Actualizar el modelo de acuerdo a la cantidad de keywords
topic_model.update_topics(
    base['lemas'].tolist(),
    vectorizer_model=topic_model.vectorizer_model,
    top_n_words=cantidad_keywords  # <-- Esto abre el grifo a 15
)
# 3. Agrego una columna con el tópico asignado al artículo
base['bertopic_tema'] = topic_model.topics_


# 4. Obtener la tabla de temas y mostrarlos en consola
info_temas = topic_model.get_topic_info()
print(info_temas)
print()

# 5. Obtener todos los temas, excepto el de outliers (-1)
temas_validos = [t for t in topic_model.get_topics().keys() if t != -1]

# 6. Recorrer temas_validos para obtener keywords y artículos
for tema in temas_validos:
    print(f"\n=== TEMA {tema} ===")
    # Palabras clave del tema
    palabras_clave = [pal for pal, _ in topic_model.get_topic(tema)[:cantidad_keywords]]
    print("Palabras clave:", ', '.join(palabras_clave))

    if mostrar_articulos == False:
        continue

    # 6.1. Calculamos la similitud de TODOS los documentos con este tema específico
    # Esto da una lista de puntuaciones de 0 a 1 para cada artículo
    similitudes = topic_model.approximate_distribution(base['texto_completo'].tolist(), window=1)[0]

    # 6.2. Agregamos temporalmente esa puntuación al DataFrame para poder ordenar
    base['puntuacion_tema'] = [sim[tema] if tema < len(sim) else 0 for sim in similitudes]

    # 6.3. Filtramos por los que pertenecen al tema y ordenamos de mayor a menor pureza
    docs_emblematicos = (
        base[base['bertopic_tema'] == tema]
        .sort_values(by='puntuacion_tema', ascending=False)
        .head(cantidad_articulos)
    )

    print("Artículos más emblemáticos (ordenados por relevancia matemática):")
    for _, fila in docs_emblematicos.iterrows():
        # Mostramos la puntuación para ver qué tan "puro" es el artículo en ese tema
        print(f"- [{fila['puntuacion_tema']:.2f}] {fila['titulo']} [{fila['medio']}]")


