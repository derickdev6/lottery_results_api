from fastapi import FastAPI, HTTPException, Header, Depends
import json
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
API_KEY = os.getenv("API_KEY", "my-secure-api-key")

# Middleware o dependencia para validar la API Key
async def validate_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

@app.get("/results", dependencies=[Depends(validate_api_key)])
async def get_results():
    try:
        with open("results.json", "r", encoding="utf-8") as file:
            results = json.load(file)
        return results
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="El archivo de resultados no existe")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error leyendo los resultados: {str(e)}")
