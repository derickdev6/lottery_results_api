import requests
import os
from fastapi import FastAPI, HTTPException, Header
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from fastapi import Depends


load_dotenv()

# Crear instancia de FastAPI
app = FastAPI()

# API Key almacenada en una variable de entorno (usa un valor fijo para pruebas locales si lo prefieres)
API_KEY = os.getenv("API_KEY", "my-secure-api-key")

# URL de la página
LOTTERY_URL = "https://www.pagatodo.com.co/resultados.php?plg=resultados-loterias"

# Diccionario de mapeo para traducir los `src` al nombre de la lotería
src_to_text_mapping = {
    "modules/mod_resultados/images/logo-1-lotcundinamarca.png?crc=4117966680": "Lotería de Cundinamarca",
    "modules/mod_resultados/images/logo-2-lottolima.png?crc=4005093239": "Lotería del Tolima",
    "modules/mod_resultados/images/logo-3-lotcruzroja.png?crc=327209619": "Lotería de la Cruz Roja",
    "modules/mod_resultados/images/logo-4-lothuila.png?crc=293622564": "Lotería de Huila",
    "modules/mod_resultados/images/logo-5-lotmeta.png?crc=3926117073": "Lotería del Meta",
    "modules/mod_resultados/images/logo-6-lotvalle.png?crc=3921251683": "Lotería del Valle",
    "modules/mod_resultados/images/logo-7-lotmanizales_2.png?crc=3953215533": "Lotería de Manizales",
    "modules/mod_resultados/images/logo-8-lotbogota.png?crc=144019873": "Lotería de Bogotá",
    "modules/mod_resultados/images/logo-9-logquindio.png?crc=3882119554": "Lotería del Quindío",
    "modules/mod_resultados/images/logo-10-lotrisaralda.png?crc=3867586460": "Lotería de Risaralda",
    "modules/mod_resultados/images/logo-11-lotmedellin.png?crc=142877452": "Lotería de Medellín",
    "modules/mod_resultados/images/logo-12-lotboyaca.png?crc=3896312962": "Lotería de Boyacá",
    "modules/mod_resultados/images/logo-13-lotsantander.png?crc=96966117": "Lotería de Santander",
    "modules/mod_resultados/images/logo-14-lotcauca.png?crc=286426838": "Lotería del Cauca",
    "modules/mod_resultados/images/logo-15-extradecolombia.png?crc=112948180": "Extra de Colombia",
}

# Middleware o dependencia para validar la API Key
async def validate_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")


@app.get("/results", dependencies=[Depends(validate_api_key)])
async def get_results():
    # Encabezados para la solicitud HTTP
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }

    # Realizar la solicitud HTTP
    response = requests.get(LOTTERY_URL, headers=headers)

    if response.status_code != 200:
        return {
            "error": f"No se pudo acceder a la página, código de estado: {response.status_code}"
        }

    # Analizar el contenido HTML
    soup = BeautifulSoup(response.text, "html.parser")

    # Buscar los bloques de resultados basados en "SERIE:"
    series_paragraphs = soup.find_all(
        "p", string=lambda text: text and "SERIE:" in text
    )

    print(f"Se encontraron {len(series_paragraphs)} bloques de resultados.")

    results = []
    for series_p in series_paragraphs:
        try:
            # Encontrar el bloque del resultado basado en la posición relativa
            block = series_p.find_parent("div").find_parent("div").find_parent("div")
            if not block:
                print("No se encontró un contenedor para este párrafo de serie.")
                continue

            # Obtener el atributo `src` de la imagen
            image_tag = block.find("img", {"class": "block"})
            src = image_tag["src"] if image_tag else None
            name = src_to_text_mapping.get(
                src, "Desconocido"
            )  # Traducir usando el diccionario

            # Extraer la fecha
            date_tag = block.find("input", {"class": "dateresul"})
            date = date_tag["value"].strip() if date_tag else "N/A"

            # Buscar el número asociado
            number_p = block.find("p", string=lambda text: text and "NÚMERO:" in text)
            result_tag = number_p.find_next("p") if number_p else None
            result = result_tag.text.strip() if result_tag else "N/A"

            # Buscar el dia que se juega la loteria
            day_tag = block.find("p", string=lambda text: text and "JUEGA" in text)
            day = day_tag.find_next("p").text.strip() if day_tag else "N/A"

            # Serie ya está identificada
            series_tag = series_p.find_next("p")
            series = series_tag.text.strip() if series_tag else "N/A"

            # Agregar al resultado
            results.append(
                {
                    "nombre_loteria": name,
                    "numero": result,
                    "numero_serie": series,
                    "fecha": date,
                    "cuando_juega": day,
                }
            )
        except Exception as e:
            # Manejar errores y continuar
            print(f"Error procesando un bloque de lotería: {e}")

    # Retornar los resultados en formato JSON
    return results
