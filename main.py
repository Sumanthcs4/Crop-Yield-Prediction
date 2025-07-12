from crop_yield.components.data_ingestion import DataIngestion
from crop_yield.components.data_validation import DataValidation
from crop_yield.exception.exception import CropYieldException
from crop_yield.logging.logger import logging
from crop_yield.entity.config_entity import TrainingPipelineConfig, DataIngestionConfig, DataValidationConfig
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

    except Exception as e:
        raise CropYieldException(e, sys)
