import os
import numpy as np

import logging

from catboost import CatBoostRegressor

class Predict():
    
    def __init__(self):

        # self.model = load(os.environ["MODEL_FILES_PATH"] + "/ranking_model.pkl")
        self.model = CatBoostRegressor()
        self.model.load_model(os.environ["MODEL_FILES_PATH"] + "/model.cbm")
    

    def predict(self, inputs):
        
        logging.info(f"✅ Inputs: {inputs}")
        
        # Extract ranking features and article IDs from the inputs
        features = inputs[0].pop("ranking_features")
        item_ids = inputs[0].pop("item_ids")

        # Make predictions
        scores = self.model.predict(features).tolist()

        return {"item_ids": item_ids, "scores": scores}
