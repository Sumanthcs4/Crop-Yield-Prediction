import os
import sys
import numpy as np
import mlflow
import mlflow.sklearn

from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error

from crop_yield.entity.artifact_entity import DataTransformationArtifact, ModelTrainerArtifact, RegressionMetricArtifact
from crop_yield.exception.exception import CropYieldException
from crop_yield.logging.logger import logging
from crop_yield.entity.config_entity import ModelTrainerConfig
from crop_yield.utils.main_utils.utils import save_object, load_object, load_numpy_array_data, evaluate_models
from crop_yield.utils.ml_utils.model.estimator import CropYieldModel


class ModelTrainer:
    def __init__(self, model_trainer_config: ModelTrainerConfig, data_transformation_artifact: DataTransformationArtifact):
        try:
            self.model_trainer_config = model_trainer_config
            self.data_transformation_artifact = data_transformation_artifact
        except Exception as e:
            raise CropYieldException(e, sys)

    def track_mlflow(self, model, train_metric: RegressionMetricArtifact, test_metric: RegressionMetricArtifact):
        try:
            # Log model name
            mlflow.log_param("model_name", type(model).__name__)

            # Log evaluation metrics
            mlflow.log_metric("train_r2_score", train_metric.r2_score)
            mlflow.log_metric("train_rmse", train_metric.rmse)
            mlflow.log_metric("train_mae", train_metric.mae)

            mlflow.log_metric("test_r2_score", test_metric.r2_score)
            mlflow.log_metric("test_rmse", test_metric.rmse)
            mlflow.log_metric("test_mae", test_metric.mae)

            # Log the model itself
            mlflow.sklearn.log_model(model, "model")

        except Exception as e:
            raise CropYieldException(e, sys)

    def evaluate_regression_model(self, model, X_train, y_train, X_test, y_test):
        try:
            y_train_pred = model.predict(X_train)
            y_test_pred = model.predict(X_test)

            train_metrics = RegressionMetricArtifact(
                r2_score=r2_score(y_train, y_train_pred),
                rmse=np.sqrt(mean_squared_error(y_train, y_train_pred)),
                mae=mean_absolute_error(y_train, y_train_pred)
            )

            test_metrics = RegressionMetricArtifact(
                r2_score=r2_score(y_test, y_test_pred),
                rmse=np.sqrt(mean_squared_error(y_test, y_test_pred)),
                mae=mean_absolute_error(y_test, y_test_pred)
            )

            return train_metrics, test_metrics

        except Exception as e:
            raise CropYieldException(e, sys)

    def train_model(self, X_train, y_train, X_val, y_val, X_test, y_test):
        try:
            models = {
                "LinearRegression": LinearRegression(),
                "DecisionTree": DecisionTreeRegressor(),
                "RandomForest": RandomForestRegressor(),
                "XGBoost": XGBRegressor()
            }

            param = {
                "DecisionTree": {
                    "max_depth": [5, 10, 15],
                    "min_samples_split": [2, 5, 10]
                },
                "RandomForest": {
                    "n_estimators": [50, 100],
                    "max_depth": [10, 20]
                },
                "XGBoost": {
                    "n_estimators": [100, 200],
                    "learning_rate": [0.03, 0.1],
                    "max_depth": [3, 6]
                },
                "LinearRegression": {}  # No hyperparameter tuning
            }

            # Evaluate all models and get best
            model_report = evaluate_models(X_train, y_train, X_val, y_val, models, param)
            best_model_name = max(model_report, key=model_report.get)
            best_model = models[best_model_name]
            best_model.fit(X_train, y_train)

            # Evaluate metrics
            train_metric, test_metric = self.evaluate_regression_model(best_model, X_train, y_train, X_test, y_test)

            # Track metrics and model with MLflow
            self.track_mlflow(best_model, train_metric, test_metric)

            # Save model wrapped with preprocessor
            preprocessor = load_object(self.data_transformation_artifact.transformed_object_file_path)
            model_dir_path = os.path.dirname(self.model_trainer_config.trained_model_file_path)
            os.makedirs(model_dir_path, exist_ok=True)

            final_model = CropYieldModel(preprocessor=preprocessor, model=best_model)
            save_object(self.model_trainer_config.trained_model_file_path, final_model)
            save_object("final_model/model.pkl", best_model)

            return ModelTrainerArtifact(
                trained_model_file_path=self.model_trainer_config.trained_model_file_path,
                train_metric_artifact=train_metric,
                test_metric_artifact=test_metric
            )

        except Exception as e:
            raise CropYieldException(e, sys)

    def initiate_model_trainer(self) -> ModelTrainerArtifact:
        try:
            train_arr = load_numpy_array_data(self.data_transformation_artifact.transformed_train_file_path)
            val_arr = load_numpy_array_data(self.data_transformation_artifact.transformed_val_file_path)
            test_arr = load_numpy_array_data(self.data_transformation_artifact.transformed_test_file_path)

            X_train, y_train = train_arr[:, :-1], train_arr[:, -1]
            X_val, y_val = val_arr[:, :-1], val_arr[:, -1]
            X_test, y_test = test_arr[:, :-1], test_arr[:, -1]

            return self.train_model(X_train, y_train, X_val, y_val, X_test, y_test)

        except Exception as e:
            raise CropYieldException(e, sys)
