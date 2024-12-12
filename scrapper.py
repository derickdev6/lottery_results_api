from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import json
import random

options = Options()
options.add_argument("--headless")  # Ejecuta sin interfaz gráfica
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1920,1080")  # Simula un tamaño de ventana completo
options.add_argument(
    "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
)  # Cambia el agente de usuario
options.set_capability(
    "goog:loggingPrefs", {"performance": "ALL"}
)  # Captura los logs de red

# Inicializa el controlador del navegador
driver = webdriver.Chrome(
    service=Service("/opt/homebrew/bin/chromedriver"),
    options=options,
)

# URL principal
URL = "https://www.pagatodo.com.co/resultados.php?plg=resultados-loterias"

# Mapeo de enlaces a nombres basado en búsqueda parcial
link_name_mapping = {
    "cundinamarca": "Lotería de Cundinamarca",
    "tolima": "Lotería del Tolima",
    "cruz-roja": "Lotería de la Cruz Roja",
    "huila": "Lotería del Huila",
    "meta": "Lotería del Meta",
    "valle": "Lotería del Valle",
    "manizales": "Lotería de Manizales",
    "bogota": "Lotería de Bogotá",
    "quindio": "Lotería del Quindío",
    "risaralda": "Lotería de Risaralda",
    "medellin": "Lotería de Medellín",
    "santander": "Lotería de Santander",
    "boyaca": "Lotería de Boyacá",
    "extra-de-colombia": "Lotería Extra de Colombia",
    "cauca": "Lotería del Cauca",
}


def get_links():
    try:
        # Leer el archivo links.json
        with open("links.json", "r", encoding="utf-8") as file:
            links_data = json.load(file)

        # Incrementar el ID de cada entrada en 1
        for entry in links_data:
            entry["id"] += 1

        # Guardar los cambios en el archivo links.json
        with open("links.json", "w", encoding="utf-8") as file:
            json.dump(links_data, file, ensure_ascii=False, indent=4)

        return [entry["base"] for entry in links_data]
    except Exception as e:
        print(f"Error al procesar links.json: {e}")
        return []


def scrape_details(links):
    results = []
    for idx, link in enumerate(links):
        print(f"Procesando enlace {idx + 1}/{len(links)}: {link}")
        driver.get(link)
        # Espera a que el contenido de la página esté cargado
        WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, "body"))
        )

        print("Esperando para respetar Crawl-delay...")
        time.sleep(random.uniform(1, 2))

        # Obtén el HTML de la página
        html = driver.page_source

        # Analiza el HTML con BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")

        try:
            # Identificar el contenedor principal
            main_div = soup.select_one("html > body > div > div > div:nth-of-type(3)")
            if not main_div:
                print(f"No se encontró el contenedor principal en el enlace {link}.")
                continue

            # Obtener todos los divs hijos del contenedor principal
            child_divs = main_div.find_all("div", recursive=False)

            # Extraer las etiquetas <p> dentro de cada div hijo
            data = []
            for child in child_divs:
                paragraphs = child.find_all("p")
                data.extend([p.text.strip() for p in paragraphs if p.text.strip()])

            # Determinar el nombre de la lotería basado en el enlace
            loteria_name = "Desconocido"
            for key, name in link_name_mapping.items():
                if key in link:
                    loteria_name = name
                    break

            # Formatear el JSON según los requisitos
            result = {
                "nombre": loteria_name,
                "fecha": data[0] if len(data) > 0 else "N/A",
                "resultado": data[1] if len(data) > 1 else "N/A",
                "serie": data[2] if len(data) > 2 else "N/A",
                "secos": [],
            }

            for i in range(3, len(data), 3):
                seco = {
                    "nombre": data[i] if i < len(data) else "N/A",
                    "resultado": data[i + 1] if i + 1 < len(data) else "N/A",
                    "serie": data[i + 2] if i + 2 < len(data) else "N/A",
                }
                result["secos"].append(seco)

            results.append(result)
        except Exception as e:
            print(f"Error al procesar {link}: {e}")
            continue
    return results


# Ejecución principal
def main():
    links = get_links()
    if links:
        print("Iniciando scraping de detalles...")
        details = scrape_details(links)
        with open("results.json", "w", encoding="utf-8") as file:
            json.dump(details, file, ensure_ascii=False, indent=4)
        print("Datos guardados en results.json")
    else:
        print("No se encontraron enlaces.")


if __name__ == "__main__":
    main()

# Cierra el navegador
driver.quit()
