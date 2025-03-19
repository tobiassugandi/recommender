import streamlit as st
import logging
from recsys.ui.utils import get_deployments
from recsys.ui.recommenders import customer_recommendations

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
USER_IDS = [
    "256843",
    "256143",
    "251843",
    "216843",
    "156843",
]

def initialize_page():
    """Initialize Streamlit page configuration"""
    st.set_page_config(layout="wide", initial_sidebar_state="expanded")
    st.title("📚 Your Book Recommendations")
    st.sidebar.title("⚙️ Configuration") # todo

def initialize_services():
    logger.info("Initializing deployments...")
    with st.sidebar:
        with st.spinner("🚀 Starting Deployments..."):
            items_fv, ranking_deployment, query_model_deployment = get_deployments()
        st.success("✅ Deployments Ready")

        # Stop deployments button
        if st.button(
            "⏹️ Stop Deployments", key="stop_deployments_button", type="secondary"
        ):
            ranking_deployment.stop()
            query_model_deployment.stop()
            st.success("Deployments stopped successfully!")

    return items_fv, ranking_deployment, query_model_deployment

def main():
    # Initialize page
    initialize_page()
    
    # Initialize services
    items_fv, ranking_deployment, query_model_deployment = (
        initialize_services()
    )

    # Select customer
    customer_id = st.sidebar.selectbox(
        "👤 Select Customer:", USER_IDS, key="selected_customer"
    )

    customer_recommendations(
        items_fv, ranking_deployment, query_model_deployment, customer_id
    )

if __name__ == "__main__":
    main()