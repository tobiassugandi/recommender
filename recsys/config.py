from pydantic import SecretStr 
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Hopsworks
    HOPSWORKS_API_KEY: SecretStr | None = None

    RECSYS_DIR: Path = Path(__file__).parent

    # Two-Tower model params
    TT_BATCH_SIZE: int = 128
    TT_EPOCHS: int = 2
    TT_LEARNING_RATE: float = 0.005
    TT_L2_REG: float = 0.001
    TT_WEIGHT_DECAY: float = 0.001
    TT_EMBEDDING_DIM: int = 16
    TT_VALIDATION_SPLIT: float = 0.1
    TT_TEST_SPLIT: float = 0.1

    # Catboost model params
    CB_ITERATIONS: int = 500
    CB_LEARNING_RATE: float = 0.05
    CB_DEPTH: int = 6
    CB_EARLY_STOPPING_ROUNDS: int = 50

    RANKING_MODEL_TYPE: str = "ranking"
    QUERY_MODEL_TYPE: str = "query"

settings = Settings()