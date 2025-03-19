import streamlit as st
import time
from .utils import (
    fetch_and_process_image,
    get_item_image_url,
    print_header,
)

def display_item(isbn, 
                 score, 
                 items_fv, 
                 user_id, 
                #  tracker, 
                #  source
                 ):
    """Display a single item with its interactions"""
    image_url = get_item_image_url(isbn, items_fv)
    # st.write(f"**🔗 [Open image in new tab]({image_url})**")
    img = fetch_and_process_image(image_url)
    if img:
        st.image(img, use_container_width=True)
    else:
        st.write("Failed to fetch and process image")
    st.write(f"**ISBN:** {isbn}")
    st.write(f"**🎯 Predicted rating:** {score:.2f}")

def customer_recommendations(
    items_fv,
    ranking_deployment,
    query_model_deployment,
    user_id,
    max_retries: int = 5,
    retry_delay: int = 60,
):
    # Initialize or update recommendations
    if "customer_recs" not in st.session_state:
        st.session_state.customer_recs = []
        # st.session_state.prediction_time = None

    # Only get new predictions if:
    # 1. Button is clicked OR
    # 2. No recommendations exist OR
    # 3. Customer ID changed
    if (
        st.sidebar.button("Get Recommendations", key="get_recommendations_button")
        or not st.session_state.customer_recs
        or "last_user_id" not in st.session_state
        or st.session_state.last_user_id != user_id
    ):
        with st.spinner("🔮 Getting recommendations..."):
            st.session_state.last_user_id = user_id

            # Get predictions from model using a retry mechanism in case of failure.
            deployment_input = [
                {"user_id": user_id, 
                #  "transaction_date": formatted_timestamp,
                 }
            ]
            warning_placeholder = None
            for attempt in range(max_retries):
                try:
                    prediction = query_model_deployment.predict(
                        inputs=deployment_input
                    )["predictions"]
                    # prediction = ranking_deployment.predict(
                    #     inputs=prediction
                    # )["predictions"]["ranking"]
                    if warning_placeholder:
                        warning_placeholder.empty()
                    break
                except Exception as e:
                    if attempt < max_retries - 1:
                        warning_placeholder = st.warning(
                            f"⚠️ Failed to call the H&M recommender QUERY deployment. It's probably scaling from 0 to +1 instances, which may take 1-2 minutes. Retrying in {retry_delay} seconds..."
                        )
                        time.sleep(retry_delay)
                    else:
                        st.error(
                            f"❌ Failed to get QUERY predictions after {max_retries} retries"
                        )
                        raise e
            
            # wait for 30 seconds
            time.sleep(retry_delay)

            for attempt in range(max_retries):
                try:
                    # prediction = query_model_deployment.predict(
                    #     inputs=deployment_input
                    # )["predictions"]
                    prediction = ranking_deployment.predict(
                        inputs=prediction
                    )["predictions"]["ranking"]
                    if warning_placeholder:
                        warning_placeholder.empty()
                    break
                except Exception as e:
                    if attempt < max_retries - 1:
                        warning_placeholder = st.warning(
                            f"⚠️ Failed to call the H&M recommender RANKING deployment. It's probably scaling from 0 to +1 instances, which may take 1-2 minutes. Retrying in {retry_delay} seconds..."
                        )
                        time.sleep(retry_delay)
                    else:
                        st.error(
                            f"❌ Failed to get RANKING predictions after {max_retries} retries"
                        )
                        raise e

            # Filter out purchased items
            available_items = [
                (isbn, score)
                for score, isbn in prediction
                # if tracker.should_show_item(user_id, isbn)
            ]
            
            # Store recommendations and extras
            st.session_state.customer_recs = available_items[:12]
            st.session_state.extra_recs = available_items[12:]

            # # Track shown items
            # tracker.track_shown_items(
            #     user_id,
            #     [(isbn, score) for isbn, score in st.session_state.customer_recs],
            # )            

            st.sidebar.success("✅ Got new recommendations")

    # Display recommendations
    print_header("📝 Top 12 Recommendations:")

    if not st.session_state.customer_recs:
        st.warning(
            "No recommendations available. Click 'Get Recommendations' to start."
        )
        return
    
    # Display items in 3x4 grid
    for row in range(3):
        cols = st.columns(4)    
        for col in range(4):
            idx = row * 4 + col
            if idx < len(st.session_state.customer_recs):
                isbn, score = st.session_state.customer_recs[idx]
                # if tracker.should_show_item(user_id, isbn):
                with cols[col]:
                    display_item(
                        isbn,
                        score,
                        items_fv,
                        user_id,
                        # tracker,
                        # "customer",
                    )
                # else:
                #     # Replace purchased item with one from extras
                #     if st.session_state.extra_recs:
                #         new_item = st.session_state.extra_recs.pop(0)
                #         st.session_state.customer_recs.append(new_item)
                #     st.session_state.customer_recs.pop(idx)
                #     st.experimental_rerun()