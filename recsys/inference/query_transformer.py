import hopsworks
import logging

import nest_asyncio
nest_asyncio.apply()

class Transformer():
    def __init__(self) -> None:
        # Connect to the Hopsworks
        project = hopsworks.login()
        fs = project.get_feature_store()

        # # Retrieve the deployed-ranking-model
        # ms = project.get_model_serving()
        # self._retrieve_secrets()
        # self.ranking_server = ms.get_deployment(self.ranking_model_type)

        # Retrieve the 'customers' feature view
        self.customer_fv = fs.get_feature_view(
            version=1,
            name="users",
        )

        # # Retrieve  the "ranking" feature view and initialize the batch scoring server.
        # self.ranking_fv = fs.get_feature_view(name="ranking", version=1)
        # self.ranking_fv.init_batch_scoring(1)


    def _retrieve_secrets(self):
        project = hopsworks.login()
        secrets_api = hopsworks.get_secrets_api()
        try:
            self.ranking_model_type = secrets_api.get_secret("RANKING_MODEL_TYPE").value
        except Exception as e:
            logging.error(e)
            logging.error("Could not retrieve secret RANKING_MODEL_TYPE, defaulting to ranker")
            self.ranking_model_type = "ranking"  

    def preprocess(self, inputs):
        # Check if the input data contains a key named "instances"
        # and extract the actual data if present
        inputs = inputs["instances"] if "instances" in inputs else inputs
        inputs = inputs[0]      

        # Extract customer_id and transaction_date from the inputs
        user_id = inputs["user_id"]
        # transaction_date = inputs["transaction_date"]

        # # Extract month from the transaction_date
        # month_of_purchase = datetsime.fromisoformat(inputs.pop("transaction_date"))

        # Get customer features
        customer_features = self.customer_fv.get_feature_vector(
            {"user_id": user_id},
            return_type="pandas",
        )

        # Enrich inputs with customer age
        # todo: add other features!!
        inputs["age"] = customer_features.age.values[0]

        # # on-demand transformation
        # # on-demand transformation
        # # on-demand transformation
        # # Calculate the sine and cosine of the month_of_purchase
        # month_of_purchase = datetime.strptime(
        #     transaction_date, "%Y-%m-%dT%H:%M:%S.%f"
        # ).month

        # # Calculate the sine and cosine components for the month_of_purchase using on-demand transformation present in "ranking" feature view.
        # feature_vector = self.ranking_fv._batch_scoring_server.compute_on_demand_features(
        #     feature_vectors=pd.DataFrame([inputs]), request_parameters={"month": month_of_purchase}
        # ).to_dict(orient="records")[0]

        # inputs["month_sin"] = feature_vector["month_sin"]
        # inputs["month_cos"] = feature_vector["month_cos"]

        return {
            "instances": [
                inputs
                ]
            }

    # def postprocess(self, outputs):
    #     # Return ordered ranking predictions
    #     return self.ranking_server.predict(inputs=outputs)
