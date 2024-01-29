if [ ${ENV} = "DEV" ]; then 
    alembic upgrade head && uvicorn api.fast:app --host 0.0.0.0 --port 8081 --env-file .env.development --ssl-certfile ./localhost.pem --ssl-keyfile ./localhost-key.pem  --reload
else
    alembic upgrade head && uvicorn api.fast:app --host 0.0.0.0 --port 8081 --env-file .env
fi