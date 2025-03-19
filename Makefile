install:
	uv venv
	. .venv/bin/activate
	uv pip install --all-extras --requirement pyproject.toml

get-data:
	curl -L -o ./book-recommendation-dataset.zip https://www.kaggle.com/api/v1/datasets/download/arashnic/book-recommendation-dataset
	unzip book-recommendation-dataset.zip -d ./data
	rm book-recommendation-dataset.zip

start-ui:
	RANKING_MODEL_TYPE=ranking uv run python -m streamlit run streamlit_app.py