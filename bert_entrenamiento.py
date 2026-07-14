idioma = 'es' # Opciones: es (español), en (inglés)

from bertopic import BERTopic
from bertopic.representation import MaximalMarginalRelevance
from sklearn.feature_extraction.text import CountVectorizer
import umap
from hdbscan import HDBSCAN
import pickle
from funciones import obtener_stop_words
import pandas as pd

minimo_articulos = 20  # Cantidad mínima de artículos que tiene que tener un tema
cantidad_temas = 10    # Cantidad aproximada de temas en que agrupará los artículos
                       # colocar "auto" si se quiere que el algoritmo lo estime

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 300)
pd.set_option('display.max_colwidth', 40)

base = pd.read_pickle('pickles/base.pkl')

base['texto_completo'] = (
    base['titulo'].fillna('') + " " +
    base['copete'].fillna('') + " " +
    base['texto'].fillna('')
)

# 1. Configuración de UMAP (optimizado para corpus pequeño de documentos)
umap_model = umap.UMAP(
    n_neighbors=10,        # Ajustado para corpus chico
    n_components=5,       # Mantiene la riqueza semántica sin saturar
    min_dist=0.05,        # Tolera clusters un poco más suaves (menos outliers)
    metric='cosine',
    random_state=42       # Para que el resultado sea reproducible
)


# 2. Configuración de eHDBSCAN (Para controlar los outliers en corpus chico)
hdbscan_model = HDBSCAN(
    min_cluster_size=minimo_articulos,
    min_samples=3,         # Menos restrictivo para no inflar los outliers
    prediction_data=True
)


# 3. Configuración del Vectorizador
vectorizer_model = CountVectorizer(
    stop_words = obtener_stop_words(idioma)
)

# 4. Inicialización de BERTopic
if idioma == 'es':
    lenguaje = 'multilingual'
elif idioma == 'en':
    lenguaje = 'english'

topic_model = BERTopic(
    umap_model=umap_model,
    hdbscan_model=hdbscan_model,
    vectorizer_model=vectorizer_model,
    nr_topics=cantidad_temas,
    language=lenguaje
)

# 5. Entrenamiento del modelo
# Pasamos la columna 'texto_completo' (titulo + copete + texto) para los EMBEDDINGS (Semántica)
# Pero extraemos las PALABRAS CLAVE desde la columna 'lemas'
docs_para_embeddings = base['texto_completo'].tolist()
docs_para_palabras_clave = base['lemas'].tolist()

topics, probs = topic_model.fit_transform(docs_para_embeddings)

# 6. Configuración de MMR para ampliar la diversidad entre tema y tema
representation_model = MaximalMarginalRelevance(diversity=0.4)

# 7. Actualización de representaciones
topic_model.update_topics(
    docs_para_palabras_clave,
    vectorizer_model=vectorizer_model,
    representation_model=representation_model # Aplica el filtro para no repetir palabras
)

# 8. Guardado en pickle
with open('pickles/modelo_bertopic.pkl', 'wb') as f:
    pickle.dump(topic_model, f)

print("¡Modelo BERTopic entrenado y guardado con éxito!")
