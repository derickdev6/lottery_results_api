import json
import boto3
from fastapi import FastAPI, HTTPException, Header, Depends
from mangum import Mangum

app = FastAPI()
API_KEY = "47SFw0COzXcwePfecOUwWUXe9BrZhg"  # Replace with your actual API key

# S3 configuration
BUCKET_NAME = "scraperjsonresult"  # Replace with your S3 bucket name
FILE_NAME = "results.json"


# Middleware or dependency to validate the API key
async def validate_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")


# Initialize S3 client
s3 = boto3.client("s3")


# Endpoint to fetch results.json from S3
@app.get("/results", dependencies=[Depends(validate_api_key)])
async def get_results():
    try:
        # Fetch the file from S3
        response = s3.get_object(Bucket=BUCKET_NAME, Key=FILE_NAME)
        file_content = response["Body"].read().decode("utf-8")
        results = json.loads(file_content)
        return results
    except s3.exceptions.NoSuchKey:
        raise HTTPException(
            status_code=404, detail="El archivo de resultados no existe en S3"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error leyendo los resultados: {str(e)}"
        )


# Wrap FastAPI app with Mangum for AWS Lambda compatibility
handler = Mangum(app)
