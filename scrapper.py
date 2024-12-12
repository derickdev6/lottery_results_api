from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import json
import random

# Diccionario de mapeo para traducir los links al nombre de la lotería
link_to_name_mapping = {
    "https://www.pagatodo.com.co/modules/mod_resultados/secos-loteria-de-cundinamarca.php?id=703": "Lotería de Cundinamarca",
    "https://www.pagatodo.com.co/modules/mod_resultados/secos-loteria-del-tolima.php?id=702": "Lotería del Tolima",
    "https://www.pagatodo.com.co/modules/mod_resultados/secos-loteria-de-la-cruz-roja.php?id=698": "Lotería de la Cruz Roja",
    "https://www.pagatodo.com.co/modules/mod_resultados/secos-loteria-del-huila.php?id=700": "Lotería del Huila",
    "https://www.pagatodo.com.co/modules/mod_resultados/secos-loteria-del-meta.php?id=697": "Lotería del Meta",
    "https://www.pagatodo.com.co/modules/mod_resultados/secos-loteria-del-valle.php?id=698": "Lotería del Valle",
    "https://www.pagatodo.com.co/modules/mod_resultados/secos-loteria-de-manizales.php?id=696": "Lotería de Manizales",
    "https://www.pagatodo.com.co/modules/mod_resultados/secos-loteria-de-bogota.php?id=689": "Lotería de Bogotá",
    "https://www.pagatodo.com.co/modules/mod_resultados/secos-loteria-del-quindio.php?id=683": "Lotería del Quindío",
    "https://www.pagatodo.com.co/modules/mod_resultados/secos-loteria-de-risaralda.php?id=696": "Lotería de Risaralda",
    "https://www.pagatodo.com.co/modules/mod_resultados/secos-loteria-de-medellin.php?id=695": "Lotería de Medellín",
    "https://www.pagatodo.com.co/modules/mod_resultados/secos-loteria-de-santander.php?id=669": "Lotería de Santander",
    "https://www.pagatodo.com.co/modules/mod_resultados/secos-loteria-de-boyaca.php?id=693": "Lotería de Boyacá",
    "https://www.pagatodo.com.co/modules/mod_resultados/secos-loteria-extra-de-colombia.php?id=143": "Lotería Extra de Colombia",
    "https://www.pagatodo.com.co/modules/mod_resultados/secos-loteria-del-cauca.php?id=695": "Lotería del Cauca",
}

# Configuración del navegador con Selenium
options = Options()
# options.add_argument("--headless")  # Ejecuta el navegador en modo sin interfaz gráfica
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("start-maximized")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# Inicializa el controlador del navegador
driver = webdriver.Chrome(options=options)

# URL principal
URL = "https://www.pagatodo.com.co/resultados.php?plg=resultados-loterias"


def get_links():
    driver.get(URL)
    try:
        print("Cargando página principal para obtener enlaces...")
        # Espera hasta que los elementos de la página estén cargados
        WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, "a"))
        )

        # Imprime el HTML actual para verificar la estructura
        html = driver.page_source
        print("HTML cargado:")
        soup = BeautifulSoup(html, "html.parser")
        # print(soup.prettify())  # Muestra HTML con formato

        # Encuentra todos los enlaces con la clase específica
        buttons = soup.find_all(
            "p", string=lambda text: text and "VER PREMIOS SECOS" in text
        )
        print(f"Se encontraron {len(buttons)} botones con enlaces.")
    except Exception as e:
        print(f"Error al cargar la página principal: {e}")
    links = []

    for button in buttons:
        parent_a = button.find_parent(
            "a", class_="nonblock nontext Button rounded-corners clearfix colelem"
        )  # Buscar la etiqueta <a> con clases específicas
        if parent_a:
            href = parent_a.get("href")  # Obtener el atributo href
            if href:
                # Modificar el texto del enlace para crear una URL completa
                if href.startswith("javascript:abrir_ventana1('../../"):
                    href = href.replace(
                        "javascript:abrir_ventana1('../../",
                        "https://www.pagatodo.com.co/",
                    ).replace("')", "")
                links.append(href)

    return links


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

            # Formatear el JSON según los requisitos
            loteria_name = link_to_name_mapping.get(link, "Desconocido")

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
