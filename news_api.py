filtro_busqueda = '"inteligencia artificial" AND (trabajo OR empleo)'
medios = "clarin.com,lanacion.com.ar,elpais.com"


from newsapi import NewsApiClient
import pandas as pd

# 1. Inicializamos el cliente con tu API Key de NewsAPI
# (Debes registrarte gratis en newsapi.org para obtenerla)
API_KEY = "" # Colocar la clave correspondiente
newsapi = NewsApiClient(api_key=API_KEY)

# 2. Definimos los parámetros de la investigación
consulta_booleana = '"inteligencia artificial" AND (trabajo OR empleo)'

articulos_lista = []

print("Iniciando consulta en NewsAPI...")

# 3. Realizamos la petición al endpoint 'everything' (archivo histórico)
try:
    response = newsapi.get_everything(
        q=filtro_busqueda,
        domains=medios,
        language='es',  # Forzamos idioma español
        sort_by='publishedAt',  # Orden cronológico (del más reciente al más antiguo)
        page_size=50,  # Cantidad de artículos por página (máx 100)
        page=2  # Traemos la primera página de prueba
    )

    # 4. Procesamos los resultados si la respuesta fue exitosa
    if response['status'] == 'ok':
        articulos = response.get('articles', [])

        for art in articulos:
            # NewsAPI anida los datos del medio en un diccionario 'source'
            source_info = art.get('source', {})

            info_articulo = {
                "fecha": art.get('publishedAt'),
                "medio": source_info.get('name'),
                "autor": art.get('author'),
                "titulo": art.get('title'),
                "copete": art.get('description'),  # NewsAPI llama 'description' al copete/snippet
                "url": art.get('url'),
                "contenido_previo": art.get('content')  # Texto truncado preliminar
            }
            articulos_lista.append(info_articulo)

    else:
        print(f"Error en la API: {response.get('message')}")

except Exception as e:
    print(f"Ocurrió un error en la conexión: {e}")

# 5. Convertimos a DataFrame de Pandas
df = pd.DataFrame(articulos_lista)

df.to_pickle('pickles/newsapi.pkl')

print(f"\n¡Prueba completada! Se recolectaron {len(df)} artículos.")

# 6. Mostramos un vistazo de los datos en la consola
if not df.empty:
    print("\nVistazo del DataFrame resultante:")
    print(df[["fecha", "medio", "titulo"]].head())