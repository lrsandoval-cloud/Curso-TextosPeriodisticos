import pandas as pd
from sickle import Sickle
from tqdm import tqdm

# Endpoint oficial de SciELO del país
URL = "https://oaipmh.scielo.org/uy/"
sickle_uy = Sickle(URL)
maximo = None # Colocar la cantidad de registros máxima o 'None' (sin entrecomillado) si no se quiere limitar

mis_revistas = [
    'ciencias psicológicas', 'cuadernos de investigación educativa', 'intercambios. dilemas y transiciones de la educación superior',
    'psicología, conocimiento y sociedad', 'páginas de educación', 'revista uruguaya de ciencia política',
    'revista de ciencias sociales', 'revista de derecho', 'revista de la facultad de derecho',
    'ciencias psicológicas', 'cuadernos de investigación educativa', 'dixit', 'humanidades', 'informatio',
    'inmediaciones de la comunicación', 'páginas de educación', 'revista uruguaya de antropología y etnografía',
    'revista uruguaya de ciencia política', 'revista de derecho (universidad católica dámaso a. larrañaga, facultad de derecho)',
    'revista de derecho'
    ]

print("COSECHA GLOBAL DE SCIELO")

# Solicitamos la lista general de registros (flujo continuo/iterador)
records = sickle_uy.ListRecords(metadataPrefix="oai_dc")

datos_articulos = []
contador_coincidencias = 0

# Iniciamos el recorrido completo sin límite superior de registros
for total_analizados, record in tqdm(enumerate(records, start=1), desc="Descargando registros", unit=' artículos', total=maximo):

    # Freno de mano para pruebas: lee los primeros registros globales indicados en maximo
    if maximo != None and total_analizados >= maximo:
        print(
            "\nSe alcanzó el límite de prueba de " + str(maximo) + " registros analizados."
        )
        break

    metadata = record.metadata
    if not metadata:
        continue

    # Extraemos el nombre de la revista desde 'source' y 'relation'
    fuentes = metadata.get("source", []) + metadata.get("relation", [])
    texto_fuente = " ".join(fuentes).lower()

    # Verificamos si el artículo pertenece a tu selección
    pertenece_a_lista = False
    revista_detectada = ""
    for revista in mis_revistas:
        if revista in texto_fuente:
            pertenece_a_lista = True
            revista_detectada = revista.title()
            break

    # Si coincide, extraemos y estructuramos los metadatos
    if pertenece_a_lista:
        titulo = metadata.get("title", [""])[0]
        autores = metadata.get("creator", [])
        resumen = metadata.get("description", [""])[0]
        fecha = metadata.get("date", [""])[0]
        palabras = metadata.get("subject", [])
        editor = metadata.get("publisher", [""])[0]
        tipo = metadata.get("type", [""])[0]
        fuente = metadata.get("source", [""])[0]
        idioma = metadata.get("language", [""])[0]
        url = metadata.get("identifier", [""])[0]

        datos_articulos.append(
            {
                "Título": titulo,
                "Autores": ", ".join(autores),
                "Resumen": resumen,
                "Fecha": fecha,
                "Revista": revista_detectada,
                "keywords" : ", ".join(palabras),
                "Editor" : editor,
                "Tipo" : tipo,
                "Fuente" : fuente,
                "Idioma" : idioma,
                "País": "Uruguay",
                "URL": url
            }
        )

        contador_coincidencias += 1

# --- FINALIZACIÓN DEL PROCESO ---
print("\n" + "=" * 60)
print("¡PROCESO DE COSECHA FINALIZADO CON ÉXITO!")
print(f"Total de registros revisados en el servidor: {total_analizados}")
print(f"Total de artículos recolectados de tus revistas: {len(datos_articulos)}")
print("=" * 60)

# Guardamos la base de datos completa en un archivo CSV
if datos_articulos:
    df = pd.DataFrame(datos_articulos)
    archivo_salida = "scielo_uy.pkl"
    df.to_pickle('pickles/' + archivo_salida)
    print(f"\nSe ha generado el archivo: '{archivo_salida}'")
else:
    print(
        "\nNo se generaron registros. Verifica las cadenas de texto de tu lista."
    )