import requests
from bs4 import BeautifulSoup
import json

# Diccionario de mapeo basado en palabras clave en los enlaces
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


# Función para realizar solicitudes con ScrapingBee
def scrapingbee_request(url, render_js=False):
    api_key = "api-key"  # Reemplazar con su propia clave de API
    scrapingbee_url = "https://app.scrapingbee.com/api/v1/"

    params = {
        "api_key": api_key,
        "url": url,
        "render_js": "true" if render_js else "false",
        "premium_proxy": "true",
    }

    response = requests.get(scrapingbee_url, params=params)
    if response.status_code == 200:
        return response.content
    else:
        print(f"Error en ScrapingBee: {response.status_code}")
        return None


# Función para obtener los enlaces de los botones "Ver premios secos"
def getlinks():
    URL = "https://www.pagatodo.com.co/resultados.php?plg=resultados-loterias"
    content = scrapingbee_request(URL, render_js=True)

    if not content:
        return []

    soup = BeautifulSoup(content, "html.parser")
    buttons = soup.find_all(
        "p", string=lambda text: text and "VER PREMIOS SECOS" in text
    )
    links = []

    for button in buttons:
        parent_a = button.find_parent(
            "a", class_="nonblock nontext Button rounded-corners clearfix colelem"
        )
        if parent_a:
            href = parent_a.get("href")
            if href:
                if href.startswith("javascript:abrir_ventana1('../../"):
                    href = href.replace(
                        "javascript:abrir_ventana1('../../",
                        "https://www.pagatodo.com.co/",
                    ).replace("')", "")
                links.append(href)

    return links


# Función para extraer datos de cada enlace
def scrape_details(links):
    results = []

    for link in links:
        content = scrapingbee_request(link, render_js=True)
        if not content:
            print(f"Error: No se pudo acceder al enlace {link}.")
            continue

        soup = BeautifulSoup(content, "html.parser")

        try:
            main_div = soup.select_one("html > body > div > div > div:nth-of-type(3)")
            if not main_div:
                print(f"No se encontró el contenedor principal en el enlace {link}.")
                continue

            child_divs = main_div.find_all("div", recursive=False)
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
            print(f"Error procesando el enlace {link}: {e}")

    return results


# Llamar a la función y obtener los enlaces
links = getlinks()

# Scraping iterativo de detalles
if links:
    print(f"Enlaces encontrados para 'Ver premios secos': {len(links)}")
    print("\nIniciando scraping de detalles...")
    details = scrape_details(links)

    with open("results.json", "w", encoding="utf-8") as file:
        json.dump(details, file, ensure_ascii=False, indent=4)

    print("\nDatos guardados en results.json")
else:
    print("No se encontraron enlaces para 'Ver premios secos'.")
