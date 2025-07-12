import os
import sys
import numpy as np
import pandas as pd
import pymongo
from typing import List
from dotenv import load_dotenv
from sklearn.model_selection import train_test_split

from crop_yield.entity.config_entity import DataIngestionConfig
from crop_yield.exception.exception import CropYieldException
from crop_yield.logging.logger import logging
from crop_yield.entity.artifact_entity import DataIngestionArtifact

load_dotenv()
MONGO_DB_URL = os.getenv("MONGO_DB_URL")


class DataIngestion:
    def __init__(self, data_ingestion_config: DataIngestionConfig):
        try:
            self.data_ingestion_config = data_ingestion_config
        except Exception as e:
            raise CropYieldException(e, sys)

    def export_collection_as_dataframe(self) -> pd.DataFrame:
        """
        Read the data from MongoDB and convert it to a Pandas DataFrame.
        """
        try:
            database_name = self.data_ingestion_config.database_name
            collection_name = self.data_ingestion_config.collection_name
            self.mongo_client = pymongo.MongoClient(MONGO_DB_URL)
            collection = self.mongo_client[database_name][collection_name]

            df = pd.DataFrame(list(collection.find()))
            if "_id" in df.columns:
                df.drop(columns=["_id"], axis=1, inplace=True)

            df.replace({"na": np.nan}, inplace=True)
            return df
        except Exception as e:
            raise CropYieldException(e, sys)

    def export_data_into_feature_store(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """
        Clean, preprocess, and save the DataFrame into the feature store as a CSV file.
        """
        try:
            # Drop rows with missing target
            dataframe = dataframe.dropna(subset=['hg/ha_yield'])

            # Median imputation
            for col in ['average_rain_fall_mm_per_year', 'pesticides_tonnes', 'avg_temp']:
                median_val = dataframe[col].median()
                dataframe[col].fillna(median_val, inplace=True)

            # IQR outlier removal
            def remove_outliers_iqr(df, cols):
                for col in cols:
                    Q1 = df[col].quantile(0.25)
                    Q3 = df[col].quantile(0.75)
                    IQR = Q3 - Q1
                    lower = Q1 - 1.5 * IQR
                    upper = Q3 + 1.5 * IQR
                    df = df[(df[col] >= lower) & (df[col] <= upper)]
                return df

            dataframe = remove_outliers_iqr(dataframe, ['hg/ha_yield', 'pesticides_tonnes', 'avg_temp'])

            # Save cleaned data to feature store
            feature_store_file_path = self.data_ingestion_config.feature_store_file_path
            os.makedirs(os.path.dirname(feature_store_file_path), exist_ok=True)
            dataframe.to_csv(feature_store_file_path, index=False, header=True)

            return dataframe
        except Exception as e:
            raise CropYieldException(e, sys)

    def split_data_as_train_test(self, dataframe: pd.DataFrame):
        """
        Split the data into train, validation, and test sets, and save them as CSV files.
        """
        try:
            train_ratio = self.data_ingestion_config.train_ratio
            val_ratio = self.data_ingestion_config.validation_ratio
            test_ratio = self.data_ingestion_config.test_ratio

            train_set, temp_set = train_test_split(
                dataframe, test_size=(1 - train_ratio), random_state=42
            )

            val_relative_ratio = val_ratio / (val_ratio + test_ratio)
            val_set, test_set = train_test_split(
                temp_set, test_size=(1 - val_relative_ratio), random_state=42
            )

            logging.info("Performed train-validation-test split on the DataFrame.")

            dir_path = os.path.dirname(self.data_ingestion_config.training_file_path)
            os.makedirs(dir_path, exist_ok=True)

            train_set.to_csv(self.data_ingestion_config.training_file_path, index=False, header=True)
            val_set.to_csv(self.data_ingestion_config.validation_file_path, index=False, header=True)
            test_set.to_csv(self.data_ingestion_config.testing_file_path, index=False, header=True)

            logging.info("Exported train, validation, and test file paths.")
        except Exception as e:
            raise CropYieldException(e, sys)

    def initiate_data_ingestion(self) -> DataIngestionArtifact:
        """
        Orchestrates the data ingestion process.
        """
        try:
            dataframe = self.export_collection_as_dataframe()
            dataframe = self.export_data_into_feature_store(dataframe)
            self.split_data_as_train_test(dataframe)

            data_ingestion_artifact = DataIngestionArtifact(
                feature_store_file_path=self.data_ingestion_config.feature_store_file_path,
                training_file_path=self.data_ingestion_config.training_file_path,
                validation_file_path=self.data_ingestion_config.validation_file_path,
                testing_file_path=self.data_ingestion_config.testing_file_path
            )

            return data_ingestion_artifact

        except Exception as e:
            raise CropYieldException(e, sys)
