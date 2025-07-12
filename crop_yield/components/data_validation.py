import os
import sys
import pandas as pd
from scipy.stats import ks_2samp
import logging

from crop_yield.entity.artifact_entity import DataIngestionArtifact, DataValidationArtifact
from crop_yield.entity.config_entity import DataValidationConfig
from crop_yield.exception.exception import CropYieldException
from crop_yield.constant.training_pipeline import SCHEMA_FILE_PATH
from crop_yield.utils.main_utils.utils import read_yaml_file, write_yaml_file

class DataValidation:
    def __init__(self, data_ingestion_artifact: DataIngestionArtifact, data_validation_config: DataValidationConfig):
        try:
            self.data_ingestion_artifact = data_ingestion_artifact
            self.data_validation_config = data_validation_config
            self.schema_config = read_yaml_file(SCHEMA_FILE_PATH)
        except Exception as e:
            raise CropYieldException(e, sys)

    @staticmethod
    def read_data(file_path) -> pd.DataFrame:
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            raise CropYieldException(e, sys)

    def validate_number_of_columns(self, dataframe: pd.DataFrame) -> bool:
        try:
            required_columns = self.schema_config["columns"]
            return len(dataframe.columns) == len(required_columns)
        except Exception as e:
            raise CropYieldException(e, sys)

    def detect_dataset_drift(self, base_df: pd.DataFrame, current_df: pd.DataFrame, threshold=0.05) -> bool:
        try:
            status = True
            report = {}
            for column in base_df.columns:
                if column in current_df.columns:
                    d1 = base_df[column]
                    d2 = current_df[column]
                    ks_result = ks_2samp(d1, d2)
                    drift_status = ks_result.pvalue < threshold
                    if drift_status:
                        status = False
                    report[column] = {
                        "p_value": float(ks_result.pvalue),
                        "drift_detected": drift_status
                    }

            drift_report_path = self.data_validation_config.drift_report_file_path
            os.makedirs(os.path.dirname(drift_report_path), exist_ok=True)
            write_yaml_file(file_path=drift_report_path, content=report)

            return status
        except Exception as e:
            raise CropYieldException(e, sys)

    def initiate_data_validation(self) -> DataValidationArtifact:
        try:
            # Read data from ingestion artifact paths
            train_df = self.read_data(self.data_ingestion_artifact.training_file_path)
            val_df = self.read_data(self.data_ingestion_artifact.validation_file_path)
            test_df = self.read_data(self.data_ingestion_artifact.testing_file_path)

            # Validate number of columns in all three sets
            for df, name in zip([train_df, val_df, test_df], ['Train', 'Validation', 'Test']):
                if not self.validate_number_of_columns(df):
                    raise ValueError(f"{name} dataset does not match schema column count.")

            # Drift detection between train and test (could also do val later)
            drift_status = self.detect_dataset_drift(train_df, test_df)

            # Save valid datasets
            os.makedirs(os.path.dirname(self.data_validation_config.valid_train_file_path), exist_ok=True)
            train_df.to_csv(self.data_validation_config.valid_train_file_path, index=False)
            val_df.to_csv(self.data_validation_config.valid_val_file_path, index=False)
            test_df.to_csv(self.data_validation_config.valid_test_file_path, index=False)

            # Return artifact
            return DataValidationArtifact(
                validation_status=drift_status,
                valid_train_file_path=self.data_validation_config.valid_train_file_path,
                valid_val_file_path=self.data_validation_config.valid_val_file_path,
                valid_test_file_path=self.data_validation_config.valid_test_file_path,
                invalid_train_file_path=None,
                invalid_val_file_path=None,
                invalid_test_file_path=None,
                drift_report_file_path=self.data_validation_config.drift_report_file_path
            )

        except Exception as e:
            raise CropYieldException(e, sys)
