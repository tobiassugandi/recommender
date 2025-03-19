import streamlit as st
from recsys import hopsworks_integration
from recsys.config import settings
import requests
from PIL import Image, UnidentifiedImageError
from io import BytesIO

def print_header(text, font_size=22):
    res = f'<span style="font-size: {font_size}px;">{text}</span>'
    st.markdown(res, unsafe_allow_html=True)

@st.cache_data()
def fetch_and_process_image(image_url, width=200, height=300):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        response = requests.get(image_url, headers=headers)
        if response.status_code == 200:
            img = Image.open(BytesIO(response.content))
        else:
            st.error("Failed to fetch image, status code: {}".format(response.status_code))
            return None
        img = img.resize((width, height), Image.LANCZOS)
        return img
    except (UnidentifiedImageError, requests.RequestException, IOError):
        st.error("Failed in fetch_and_process_image()")
        return None

def get_item_image_url(isbn, items_fv):
    try:
        item_df = items_fv.get_feature_vector({"isbn": isbn}, 
                                            return_type="pandas")
        return item_df["image_url_l"].values[0]
    except:
        return None


@st.cache_resource()
def get_deployments():
    project, fs = hopsworks_integration.get_feature_store()

    ms = project.get_model_serving()

    items_fv = fs.get_feature_view(
        name="items",
        version=1,
    )

    query_model_deployment = ms.get_deployment(
        settings.QUERY_MODEL_TYPE
    )

    ranking_deployment = ms.get_deployment(
        settings.RANKING_MODEL_TYPE
    )

    query_model_deployment.start(await_running=180)
    ranking_deployment.start(await_running=280)

    return items_fv, ranking_deployment, query_model_deployment
