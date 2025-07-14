import sys
import os
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer

from crop_yield.constant.training_pipeline import TARGET_COLUMN
from crop_yield.entity.artifact_entity import DataTransformationArtifact, DataValidationArtifact
from crop_yield.entity.config_entity import DataTransformationConfig
from crop_yield.exception.exception import CropYieldException
from crop_yield.logging.logger import logging
from crop_yield.utils.main_utils.utils import save_numpy_array_data, save_object


class DataTransformation:
    def __init__(self, data_validation_artifact: DataValidationArtifact,
                 data_transformation_config: DataTransformationConfig):
        try:
            self.data_validation_artifact = data_validation_artifact
            self.data_transformation_config = data_transformation_config
        except Exception as e:
            raise CropYieldException(e, sys)

    @staticmethod
    def read_data(file_path) -> pd.DataFrame:
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            raise CropYieldException(e, sys)

    def get_data_transformer_object(self, schema_config: dict) -> ColumnTransformer:
        try:
            numerical_columns = schema_config["numerical_columns"]
            categorical_columns = schema_config["categorical_columns"]

            # Remove 'Area' from one-hot encoding
            categorical_columns = [col for col in categorical_columns if col != "Area"]

            num_pipeline = Pipeline([
                ("scaler", StandardScaler())
            ])

            cat_pipeline = Pipeline([
                ("onehot", OneHotEncoder(handle_unknown='ignore'))
            ])

            preprocessor = ColumnTransformer([
                ("num_pipeline", num_pipeline, numerical_columns),
                ("cat_pipeline", cat_pipeline, categorical_columns)
            ])

            return preprocessor
        except Exception as e:
            raise CropYieldException(e, sys)

    def initiate_data_transformation(self, schema_config: dict) -> DataTransformationArtifact:
        try:
            logging.info("Reading validated datasets")
            train_df = self.read_data(self.data_validation_artifact.valid_train_file_path)
            val_df = self.read_data(self.data_validation_artifact.valid_val_file_path)
            test_df = self.read_data(self.data_validation_artifact.valid_test_file_path)

            logging.info("Splitting features and target")
            input_feature_train_df = train_df.drop(columns=[TARGET_COLUMN], axis=1)
            target_feature_train_df = train_df[TARGET_COLUMN]

            input_feature_val_df = val_df.drop(columns=[TARGET_COLUMN], axis=1)
            target_feature_val_df = val_df[TARGET_COLUMN]

            input_feature_test_df = test_df.drop(columns=[TARGET_COLUMN], axis=1)
            target_feature_test_df = test_df[TARGET_COLUMN]

            # ✅ Frequency encode 'Area' and save area_freq_map
            area_freq_map = input_feature_train_df['Area'].value_counts().to_dict()
            mean_freq = np.mean(list(area_freq_map.values()))

            for df in [input_feature_train_df, input_feature_val_df, input_feature_test_df]:
                df['Area'] = df['Area'].map(area_freq_map).fillna(mean_freq)

            # ✅ Save the area_freq_map for use during inference
            save_object("final_model/area_freq_map.pkl", area_freq_map)

            preprocessor = self.get_data_transformer_object(schema_config)

            logging.info("Fitting and transforming train data")
            preprocessor_object = preprocessor.fit(input_feature_train_df)
            transformed_input_train_feature = preprocessor_object.transform(input_feature_train_df)
            transformed_input_val_feature = preprocessor_object.transform(input_feature_val_df)
            transformed_input_test_feature = preprocessor_object.transform(input_feature_test_df)

            logging.info("Combining features with target")
            train_arr = np.c_[transformed_input_train_feature, np.array(target_feature_train_df)]
            val_arr = np.c_[transformed_input_val_feature, np.array(target_feature_val_df)]
            test_arr = np.c_[transformed_input_test_feature, np.array(target_feature_test_df)]

            logging.info("Saving transformed datasets")
            save_numpy_array_data(self.data_transformation_config.transformed_train_file_path, array=train_arr)
            save_numpy_array_data(self.data_transformation_config.transformed_val_file_path, array=val_arr)
            save_numpy_array_data(self.data_transformation_config.transformed_test_file_path, array=test_arr)

            logging.info("Saving preprocessing object")
            save_object(self.data_transformation_config.transformed_object_file_path, preprocessor_object)
            save_object("final_model/preprocessor.pkl", preprocessor_object)

            logging.info("Creating transformation artifact")
            return DataTransformationArtifact(
                transformed_object_file_path=self.data_transformation_config.transformed_object_file_path,
                transformed_train_file_path=self.data_transformation_config.transformed_train_file_path,
                transformed_val_file_path=self.data_transformation_config.transformed_val_file_path,
                transformed_test_file_path=self.data_transformation_config.transformed_test_file_path
            )

        except Exception as e:
            raise CropYieldException(e, sys)