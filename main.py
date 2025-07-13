from crop_yield.components.data_ingestion import DataIngestion
from crop_yield.components.data_validation import DataValidation
from crop_yield.components.data_transformation import DataTransformation
from crop_yield.exception.exception import CropYieldException
from crop_yield.logging.logger import logging
from crop_yield.entity.config_entity import TrainingPipelineConfig, DataIngestionConfig, DataValidationConfig, DataTransformationConfig, ModelTrainerConfig
from crop_yield.constant.training_pipeline import SCHEMA_FILE_PATH
from crop_yield.utils.main_utils.utils import read_yaml_file
from crop_yield.components.model_trainer import ModelTrainer
import sys


if __name__ == '__main__':
    try:
        logging.info("Creating training pipeline config")
        training_pipeline_config = TrainingPipelineConfig()

        logging.info("Creating data ingestion config")
        data_ingestion_config = DataIngestionConfig(training_pipeline_config)

        logging.info("Initializing data ingestion component")
        data_ingestion = DataIngestion(data_ingestion_config)

        logging.info("Starting data ingestion process")
        data_ingestion_artifact = data_ingestion.initiate_data_ingestion()
        logging.info("Data ingestion completed successfully")
        print(data_ingestion_artifact)

        logging.info("Creating data validation config")
        data_validation_config = DataValidationConfig(training_pipeline_config)

        logging.info("Initializing data validation component")
        data_validation = DataValidation(data_ingestion_artifact, data_validation_config)

        logging.info("Starting data validation process")
        data_validation_artifact = data_validation.initiate_data_validation()
        logging.info("Data validation completed successfully")
        print(data_validation_artifact)
        logging.info("Data Transformation process started")
        data_transformation_config = DataTransformationConfig(training_pipeline_config)
        data_transformation = DataTransformation(data_validation_artifact, data_transformation_config)

        # read schema
        schema_config = read_yaml_file(SCHEMA_FILE_PATH)

        # run transformation
        data_transformation_artifact = data_transformation.initiate_data_transformation(schema_config=schema_config)

        logging.info("Data Transformation completed successfully")
        print(data_transformation_artifact)
        
        logging.info("Model Training started")
        model_trainer_config=ModelTrainerConfig(training_pipeline_config)
        model_trainer=ModelTrainer(model_trainer_config=model_trainer_config,data_transformation_artifact=data_transformation_artifact)
        model_trainer_artifact=model_trainer.initiate_model_trainer()

        logging.info("Model Training artifact created")
        logging.info(f"Model Trainer Artifact: {model_trainer_artifact}")
    except Exception as e:
        raise CropYieldException(e, sys)
