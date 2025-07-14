import sys
import os
import pandas as pd
import numpy as np
import pymongo
import certifi
ca = certifi.where()
from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, JSONResponse
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse
from uvicorn import run as app_run
from pydantic import BaseModel

# Load MongoDB URL
load_dotenv()
mongo_db_url = os.getenv("MONGO_DB_URL")

# Project Imports
from crop_yield.exception.exception import CropYieldException
from crop_yield.logging.logger import logging
from crop_yield.utils.main_utils.utils import load_object
from crop_yield.utils.ml_utils.model.estimator import CropYieldModel
from crop_yield.pipeline.training_pipeline import TrainingPipeline
from crop_yield.constant.training_pipeline import DATA_INGESTION_DATABASE_NAME, DATA_INGESTION_COLLECTION_NAME

# MongoDB connection
client = pymongo.MongoClient(mongo_db_url, tlsCAFile=ca)
database = client[DATA_INGESTION_DATABASE_NAME]
collection = database[DATA_INGESTION_COLLECTION_NAME]

# FastAPI setup
app = FastAPI()
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
templates = Jinja2Templates(directory="./templates")

@app.get("/", tags=["authentication"])
async def index():
    return RedirectResponse(url="/docs")

@app.get("/train")
async def train_route():
    try:
        train_pipeline = TrainingPipeline()
        train_pipeline.run_pipeline()
        return Response("Training is successful")
    except Exception as e:
        raise CropYieldException(e, sys)


# ✅ BATCH PREDICTION ROUTE
@app.post("/predict-batch", tags=["Prediction"])
async def predict_batch_route(request: Request, file: UploadFile = File(...)):
    try:
        df = pd.read_csv(file.file)

        area_freq_map = load_object("final_model/area_freq_map.pkl")
        mean_freq = np.mean(list(area_freq_map.values()))
        df['Area'] = df['Area'].map(area_freq_map).fillna(mean_freq)

        preprocessor = load_object("final_model/preprocessor.pkl")
        model = load_object("final_model/model.pkl")

        crop_yield_model = CropYieldModel(preprocessor=preprocessor, model=model)
        predictions = crop_yield_model.predict(df)

        df["Predicted_Yield"] = predictions
        df.to_csv("prediction_output/output.csv", index=False)

        table_html = df.to_html(classes='table table-striped', index=False)
        return templates.TemplateResponse("table.html", {"request": request, "table": table_html})

    except Exception as e:
        raise CropYieldException(e, sys)


# ✅ SINGLE PREDICTION ROUTE
class SinglePredictionInput(BaseModel):
    Area: str
    Crop: str
    Season: str
    Year: int
    Item: str
    average_rain_fall_mm_per_year: float
    pesticides_tonnes: float
    avg_temp: float

@app.post("/predict", tags=["Prediction"])
async def predict_single(input_data: SinglePredictionInput):
    try:
        data = input_data.dict()
        df = pd.DataFrame([data])

        area_freq_map = load_object("final_model/area_freq_map.pkl")
        mean_freq = np.mean(list(area_freq_map.values()))
        df['Area'] = df['Area'].map(area_freq_map).fillna(mean_freq)

        preprocessor = load_object("final_model/preprocessor.pkl")
        model = load_object("final_model/model.pkl")

        crop_yield_model = CropYieldModel(preprocessor=preprocessor, model=model)
        prediction = crop_yield_model.predict(df)[0]

        return JSONResponse(content={"Predicted_Yield": prediction})

    except Exception as e:
        raise CropYieldException(e, sys)


if __name__ == "__main__":
    app_run(app, host="0.0.0.0", port=8000)
