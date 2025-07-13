import os
import sys
import numpy as np
import pandas as pd



"""defining common contant variables for training pipeline"""


TARGET_COLUMN: str = "hg/ha_yield"
TRAINING_PIPELINE_NAME: str = "crop_yield"
ARTIFACT_DIR: str = "artifacts"
FILE_NAME: str = "crop_yield.csv"

TRAIN_FILE_NAME: str = "train.csv"
VALIDATION_FILE_NAME: str = "validation.csv"
TEST_FILE_NAME: str = "test.csv"

SCHEMA_FILE_PATH: str = os.path.join("data_schema", "schema.yaml")

SAVED_MODEL_DIR: str = os.path.join("saved_models")
MODEL_FILE_NAME = "model.pkl"

"""data ingestion related constants start with 'DATA_INGESTION_'var names"""

# MongoDB settings
DATA_INGESTION_COLLECTION_NAME: str = "crop_yield_data"
DATA_INGESTION_DATABASE_NAME: str = "crop_yield"

# Directory settings
DATA_INGESTION_DIR_NAME: str = "data_ingestion"
DATA_INGESTION_FEATURE_STORE_DIR: str = "feature_store"
DATA_INGESTION_INGESTED_DIR: str = "ingested"

# Split ratios 
DATA_INGESTION_TRAIN_RATIO: float = 0.6
DATA_INGESTION_VALIDATION_RATIO: float = 0.2
DATA_INGESTION_TEST_RATIO: float = 0.2

"""
Data Validation related contsant start with DATA_VALIDATION VAR NAME
    
"""

DATA_VALIDATION_DIR_NAME: str = "data_validation"
DATA_VALIDATION_VALID_DIR: str = "validated"
DATA_VALIDATION_INVALID_DIR: str = "invalid"
DATA_VALIDATION_DRIFT_REPORT_DIR: str = "drift_report"
DATA_VALIDATION_DRIFT_REPORT_FILE_NAME: str = "report.yaml"
#PREPROCESSING_OBJECT_FILE_NAME:str = "preprocessing.pkl"

 
DATA_TRANSFORMATION_DIR_NAME = "data_transformation"
DATA_TRANSFORMATION_TRANSFORMED_DATA_DIR = "transformed"
DATA_TRANSFORMATION_TRANSFORMED_OBJECT_DIR = "preprocessing"
PREPROCESSING_OBJECT_FILE_NAME = "preprocessing.pkl"


"""
Model Trainer related constants start with MODEL_TRAINER_
"""

MODEL_TRAINER_DIR_NAME: str = "model_trainer"
MODEL_TRAINER_TRAINED_MODEL_DIR: str = "trained_model"
MODEL_TRAINER_TRAINED_MODEL_NAME: str = "model.pkl"
MODEL_TRAINER_EXPECTED_SCORE: float = 0.6
MODEL_TRAINER_OVER_FITTING_UNDER_FITTING_THRESHOLD: float = 0.05



