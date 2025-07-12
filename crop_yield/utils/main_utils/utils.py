import yaml
import os,sys
import pickle
import dill
import numpy as np
from crop_yield.exception.exception import CropYieldException
from crop_yield.logging.logger import logging



def read_yaml_file(file_path: str) -> dict:
    """
    Reads a YAML file and returns its content as a dictionary.
    """
    try:
        with open(file_path, 'r') as yaml_file:   
            return yaml.safe_load(yaml_file)
    except Exception as e:
        raise CropYieldException(e, sys) from e

def write_yaml_file(file_path: str, content: object, replace: bool = False) -> None:
    try:
        if replace:
            if os.path.exists(file_path):
                os.remove(file_path)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w") as file:
            yaml.dump(content, file)
    except Exception as e:
        raise CropYieldException(e, sys)