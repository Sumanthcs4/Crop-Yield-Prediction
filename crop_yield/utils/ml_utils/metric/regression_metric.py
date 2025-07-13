import sys
from crop_yield.entity.artifact_entity import RegressionMetricArtifact
from crop_yield.exception.exception import CropYieldException
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
import numpy as np


def get_regression_score(y_true, y_pred) -> RegressionMetricArtifact:
    try:
        model_r2_score = r2_score(y_true, y_pred)
        model_rmse = np.sqrt(mean_squared_error(y_true, y_pred))
        model_mae = mean_absolute_error(y_true, y_pred)

        regression_metric = RegressionMetricArtifact(
            r2_score=model_r2_score,
            rmse=model_rmse,
            mae=model_mae
        )
        return regression_metric
    except Exception as e:
        raise CropYieldException(e, sys)
