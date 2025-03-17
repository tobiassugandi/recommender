import logging

import hopsworks
import pandas as pd

import nest_asyncio
nest_asyncio.apply()

class Transformer(object):
    def __init__(self):
        # Connect to Hopsworks
        project = hopsworks.login()
        self.fs = project.get_feature_store()

        # todo: get from rating feature view, but pop the ratings
        self.rating_features = ["user_id", "isbn", "age", "year_of_publication"]

        # Retrieve the 'candidate_embeddings' feature view
        self.candidate_index = self.fs.get_feature_view(
            version=1,
            name="candidate_embeddings",
        )

        # Retrieve the 'ratings' feature group
        self.ratings_fg = self.fs.get_feature_group(
            version=1,
            name="ratings",
        )

        self.items_fg = self.fs.get_feature_group(name="items", version=1)
        self.users_fg = self.fs.get_feature_group(name="users", version=1)

        self.users_fv = self.fs.get_or_create_feature_view(
            version=1,
            name="users",
            query=self.users_fg.select_all(),
            description="users_feature_view",
        )

    def preprocess(self, inputs):

        # Extract the input instance
        inputs = inputs["instances"][0]

        # Extract customer_id from inputs
        user_id = inputs["user_id"]

        # Search for neighbors in the candidate index
        neighbors = self.candidate_index.find_neighbors(
            inputs["query_emb"],
            k=100,
        )
        neighbors = [neighbor[0].decode('utf-8') for neighbor in neighbors]

        # Get IDs of items already bought by the customer
        already_bought_items_ids = (
            self.ratings_fg.select("isbn")
            .filter(self.ratings_fg.user_id==user_id)
            .read(dataframe_type="pandas").values.reshape(-1)
            .tolist()
        )

        # Filter candidate items to exclude those already bought by the customer
        item_id_list = [
            str(item_id)
            for item_id in neighbors
            if str(item_id) not in already_bought_items_ids
        ]

        # Get item features for the candidate items
        ranking_model_inputs_df = (
            self.items_fg.select_all()
            .filter(self.items_fg.isbn.isin(item_id_list))
            .read(dataframe_type="pandas")
        )

        logging.info("✅ Articles Data Retrieved!")

        # Add customer features
        user_features = self.users_fv.get_feature_vector(
                {"user_id": user_id},
                return_type="pandas",
            )
        
        ranking_model_inputs_df["user_id"] = user_id
        ranking_model_inputs_df = ranking_model_inputs_df.merge(
                                    user_features, 
                                    on="user_id",
                                    how="inner")
        
        ranking_model_inputs_df = ranking_model_inputs_df[self.rating_features]

        logging.info("✅ Inputs are ready!")

        return {
            "inputs": [
                {
                    "ranking_features": ranking_model_inputs_df.values.tolist(),
                    "item_ids": item_id_list,
                }
            ]
        }

    def postprocess(self, outputs):
        logging.info("✅ Predictions are ready!")

        # Merge prediction scores and corresponding article IDs into a list of tuples
        ranking = list(zip(outputs["scores"], outputs["item_ids"]))

        # Sort the ranking list by score in descending order
        ranking.sort(reverse=True)

        # Return the sorted ranking list
        return {
            "ranking": ranking,
        }
