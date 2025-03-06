import csv
import requests
from bs4 import BeautifulSoup

def obtener_html(url):
    try:
        # Configuracion del User-Agent para evitar bloqueos de las paginas web.
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebkit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        # Realizar la peticion GET
        respuesta = requests.get(url, headers=headers, timeout=10)

        # Verificar si la respuesta fue exitosa
        if respuesta.status_code == 200:
            return respuesta.text
        else:
            print(f"Error al obtener la pagina: Codigo de estado {respuesta.status_code}")
            return None
        
    except Exception as e:
        print(f"Error al obtener la pagina: {e}")
        return None
    
def extraer_titulos_noticias(html):
    # Crear el objeto de BeautifulSoup para analizar HTML
    soup = BeautifulSoup(html, 'html.parser')

    # NOTA IMPORTANTE: Estos selectores son genericos y pueden variar y pueden necesitar ajustes segun el sitio web !OJO TENERLO PRESENTE!
    titulos = []

    # buscamos los elementos que gusten h1, h2, h3 para extraer informacion 
    for heading in soup.find_all(['h1', 'h2', 'h3']):
        # Filtrar solo lo que parecen ser titulos de noticias ( con cierta longitud)
        if heading.text.strip() and len(heading.text.strip()) > 20:
            titulos.append(heading.text.strip())

    # buscamos tambien elementos con clases comunes para titulos de noticias (!OJO ESTA APP LA ESTOY HACIENDO ENFOCADA EN NOTICIAS, LO PUEDES HACER ENFOCADA EN CUALQUEIR COSA !!)
    for elementos in soup.select('.title, .headline, .article-title, .news-title'):
        if elementos.text.strip() and elementos.text.strip() not in titulos:
            titulos.append(elementos.text.strip())
    
    return titulos

def extraer_articulos(html):
    # Crear objeto de BeautifulSoup para analizar HTML
    soup = BeautifulSoup(html, 'html.parser')

    #Lista para almacenar los articulos
    articulos = []
    
    # NOTA IMPORTANTE: Estos selectores son genericos y pueden variar y pueden necesitar ajustes segun el sitio web !OJO TENERLO PRESENTE!

    for articulos_elem in soup.select('article, .article, .post, .news-item'):
        articulo = {}

        #Extraer titulo
        titulo_elem = articulos_elem.find(['h1', 'h2', 'h3']) or articulos_elem.select_one('.title, .headline')
        if titulo_elem:
            articulo['titulo'] = titulo_elem.text.strip()
        else:
            continue # Si no hay titulos, pasar al siguiente
        
        # Extraer fecha si esta disponible
        fecha_elem = articulos_elem.select_one('.date, .time, .published, .timestamp')
        articulo['fecha'] = fecha_elem.text.strip() if fecha_elem else ""

        # Extraer resumen si esta disponible
        resumen_elem = articulos_elem.select_one('.summary, .excerpt, .description, .snippet, p')
        articulo['resumen'] = resumen_elem.text.strip() if resumen_elem else ""

        # Añadir a la lista de articulos
        articulos.append(articulo)

    return articulos

def guardar_en_csv(datos, nombre_archivo):
    try:
        # Verificar que hay en los datos para guardar
        if not datos:
            print("No hay datos para guardar")
            return False
        
        # Obtener los nombres de las columnas del primer diccionario
        columnas = datos[0].keys()

        # Escribir en el archivo CSV
        with open(nombre_archivo, 'w', newline='', encoding='utf-8') as archivo_csv:
            writer = csv.DictWriter(archivo_csv, fieldnames=columnas)
            writer.writeheader() # Escribir encabezados
            writer.writerows(datos) # Escribir filas de datos

        print(f"Datos guardados exitosamente en '{nombre_archivo}'")
        return True
    
    except Exception as e :
        print(f"Error al guardar en CSV: {e}")
        return False
    

def main():
    """Funcion principal del programa"""
    print("=== WEB SCRAPER ===")
    # Solicitar la URL al usuario
    url = input("Ingresa la URL de la pagina web a analizar o extraer datos: ")

    # Obtener el HTML de la pagina
    print(f"Descargando contenido de {url}...")
    html = obtener_html(url)

    if not html:
        print("No se pudo obtener el contenido de la pagina")
        return
     
    print ("Contenido descargado correctamente.")

    # Menu de opciones
    print("\nOpciones")
    print("1. Extraer titulos de noticias")
    print("2. Extraer articulos completos")

    opcion = input ("\nSelecciona una opcion (1-2): ")

    if opcion == "1":
        # Extraer titulos de noticias
        print("\nExtrayendo titulos de noticias ...")
        titulos = extraer_titulos_noticias(html)

        print(f"\nSe encontraron {len(titulos)} titulos:")
        for i, titulo in enumerate(titulos, 1):
            print(f"{i}. {titulo}")

        # Guardar en CSV
        if titulos and input("\n¿Deseas guardar los titulos en un archivo CSV? (s/n): ").lower() == 's':
            # Convertir la lista de titulos en forma de lista de diccionario
            datos = [{'numero': i, 'titulo': titulo} for i, titulo in enumerate(titulos, 1)]
            guardar_en_csv(datos, "titulos_noticias.csv")

    elif opcion == "2":
        # Extraer articulos
        print("\nExtrayendo articulos ...")
        articulos = extraer_articulos(html)

        print(f"\nSe encontraron {len(articulos)} articulos.")
        for i, articulos in enumerate(articulos, 1):
            print(f"{i}. {articulos.get('titulo', 'Sin titulo')}")
            if articulos.get('fecha'):
                print(f"   Fecha: {articulos['fecha']}")
            if articulos.get('resumen'):
                print(f"   Resumen: {articulos['resumen'][:100]}...")

        # Guardar en CSV
        if articulos and input("\n¿Deseas guardar los articulos en un archivo CSV? (s/n): ").lower() == 's':
            guardar_en_csv(articulos, "articulos.csv")

    else:
        print("Opcion no valida.")

if __name__ == "__main__":
    main()




    

