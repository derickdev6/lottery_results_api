import requests
from bs4 import BeautifulSoup
import json
import boto3
from botocore.exceptions import BotoCoreError, ClientError

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

# AWS S3 bucket configuration
BUCKET_NAME = "scraperjsonresult"  # Replace with your S3 bucket name
FILE_NAME = "results.json"


# Function to upload the JSON file to S3
def upload_to_s3(file_content, bucket, file_name):
    s3 = boto3.client("s3")
    try:
        s3.put_object(
            Bucket=bucket,
            Key=file_name,
            Body=file_content,
            ContentType="application/json",
            ACL="public-read",  # Optional: Set access control
        )
        print(f"File uploaded to S3: s3://{bucket}/{file_name}")
    except (BotoCoreError, ClientError) as e:
        print(f"Error uploading to S3: {e}")


# Function for ScrapingBee requests
def scrapingbee_request(url, render_js=False):
    api_key = "api-key"  # Replace with your own API key
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
        print(f"Error in ScrapingBee: {response.status_code}")
        return None


# Function to get links from "Ver premios secos"
def getlinks():
    URL = "https://www.pagatodo.com.co/resultados.php?plg=resultados-loterias"
    content = scrapingbee_request(URL, render_js=True)

    if not content:
        return []

    soup = BeautifulSoup(content, "html.parser")
    buttons = soup.find_all(
        "p", string=lambda text: text and "VER PREMIOS SECOS" in text  # type: ignore
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


# Function to scrape details from each link
def scrape_details(links):
    results = []

    for link in links:
        content = scrapingbee_request(link, render_js=True)
        if not content:
            print(f"Error: Could not access link {link}.")
            continue

        soup = BeautifulSoup(content, "html.parser")

        try:
            main_div = soup.select_one("html > body > div > div > div:nth-of-type(3)")
            if not main_div:
                print(f"Main container not found for link {link}.")
                continue

            child_divs = main_div.find_all("div", recursive=False)
            data = []
            for child in child_divs:
                paragraphs = child.find_all("p")
                data.extend([p.text.strip() for p in paragraphs if p.text.strip()])

            # Determine the lottery name based on the link
            loteria_name = "Unknown"
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
            print(f"Error processing link {link}: {e}")

    return results


# Lambda handler function
def lambda_handler(event, context):
    links = getlinks()

    if links:
        print(f"Found {len(links)} links for 'Ver premios secos'.")
        details = scrape_details(links)

        # Convert results to JSON and upload to S3
        json_content = json.dumps(details, ensure_ascii=False, indent=4)
        upload_to_s3(json_content, BUCKET_NAME, FILE_NAME)
        return {"statusCode": 200, "body": "Data successfully uploaded to S3"}
    else:
        print("No links found for 'Ver premios secos'.")
        return {"statusCode": 500, "body": "No data to upload"}
