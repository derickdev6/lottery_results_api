#!/bin/bash
# source .env
uvicorn main:app --host 0.0.0.0 --port $PORT
