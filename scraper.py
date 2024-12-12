import requests
from bs4 import BeautifulSoup
import json
import time
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

# Lista de proxies (puedes agregar más proxies aquí)
proxies_list = [
    "198.23.239.134:6540:rhcmqxze:ezyrjl46w73n",
    "207.244.217.165:6712:rhcmqxze:ezyrjl46w73n",
    "107.172.163.27:6543:rhcmqxze:ezyrjl46w73n",
    "64.137.42.112:5157:rhcmqxze:ezyrjl46w73n",
    "173.211.0.148:6641:rhcmqxze:ezyrjl46w73n",
    "161.123.152.115:6360:rhcmqxze:ezyrjl46w73n",
    "167.160.180.203:6754:rhcmqxze:ezyrjl46w73n",
    "154.36.110.199:6853:rhcmqxze:ezyrjl46w73n",
    "173.0.9.70:5653:rhcmqxze:ezyrjl46w73n",
    "173.0.9.209:5792:rhcmqxze:ezyrjl46w73n",
    # Agrega más proxies según lo necesites
]


# Función para convertir el proxy en el formato que necesita requests
def get_proxy(proxy_string):
    parts = proxy_string.split(":")
    ip = parts[0]
    port = parts[1]
    username = parts[2]
    password = parts[3]

    proxy_url = f"http://{username}:{password}@{ip}:{port}"
    return {"http": proxy_url, "https": proxy_url}


# Función para obtener los enlaces de los botones "Ver premios secos"
def getlinks():
    URL = "https://www.pagatodo.com.co/resultados.php?plg=resultados-loterias"

    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/114.0.0.0 Safari/537.36"
        ),
        "Referer": "https://www.pagatodo.com.co/",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "es-CO,es;q=0.9,en;q=0.8",
        "Connection": "keep-alive",
    }

    # Seleccionamos un proxy aleatorio
    proxy_string = random.choice(proxies_list)
    proxy = get_proxy(proxy_string)

    print(f"Usando proxy: {proxy_string}")
    # Realizar la solicitud HTTP con proxy
    response = requests.get(URL, headers=HEADERS, proxies=proxy)
    if response.status_code != 200:
        print(
            f"Error: No se pudo acceder a la página. Código de estado: {response.status_code}"
        )
        return []

    soup = BeautifulSoup(response.content, "html.parser")

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
    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/114.0.0.0 Safari/537.36"
        )
    }

    for link in links:
        print(f"Procesando enlace {link}...")
        time.sleep(random.uniform(2, 5))  # Pausa aleatoria entre 10-15 segundos

        # Seleccionamos un proxy aleatorio
        proxy = {
            "http": random.choice(proxies_list),
            "https": random.choice(proxies_list),
        }

        response = requests.get(link, headers=HEADERS, proxies=proxy)
        if response.status_code != 200:
            print(
                f"Error: No se pudo acceder al enlace {link}. Código de estado: {response.status_code}"
            )
            continue

        soup = BeautifulSoup(response.content, "html.parser")

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
            print(f"Error procesando el enlace {link}: {e}")

    return results


# Llamar a la función y obtener los enlaces
links = getlinks()

# Scraping iterativo de detalles
if links:
    print(f"Enlaces encontrados para 'Ver premios secos':{len(links)}")

    print("\nIniciando scraping de detalles...")
    details = scrape_details(links)

    # Guardar resultados en un archivo JSON
    with open("results.json", "w", encoding="utf-8") as file:
        json.dump(details, file, ensure_ascii=False, indent=4)

    print("\nDatos guardados en results.json")
else:
    print("No se encontraron enlaces para 'Ver premios secos'.")
