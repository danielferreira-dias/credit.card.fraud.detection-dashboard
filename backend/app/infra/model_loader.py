from pathlib import Path
import joblib
from typing import Any, Optional, Tuple

class Artifacts:
    scaler: Any
    model: Any
    pipe: Any

class ModelLoader:
    _artifacts: Optional[Artifacts] = None

    @classmethod
    def load(cls) -> Artifacts:
        if cls._artifacts is not None:
            return cls._artifacts

        # Caminhos relativos ao ficheiro (para Docker e local)
        base = Path(__file__).resolve().parents[1]  # -> app/
        misc = base / "misc"

        scaler_path = Path.getenv("SCALER_PATH") if hasattr(Path, "getenv") else None
        model_path  = Path.getenv("MODEL_PATH") if hasattr(Path, "getenv") else None
        pipe_path  = Path.getenv("PIPE_PATH") if hasattr(Path, "getenv") else None

        scaler_pkl = Path(scaler_path) if scaler_path else misc / "fraud_detection_scaler.pkl"
        model_pkl  = Path(model_path)  if model_path  else misc / "fraud_detection_model.pkl"
        pipe_joblib  = Path(model_path)  if pipe_path  else misc / "pipeline_xgb.joblib"

        if not scaler_pkl.exists():
            raise FileNotFoundError(f"Scaler não encontrado: {scaler_pkl}")
        if not model_pkl.exists():
            raise FileNotFoundError(f"Modelo não encontrado: {model_pkl}")
        if not pipe_joblib.exists():
            raise FileNotFoundError(f"Modelo não encontrado: {pipe_joblib}")

        scaler = joblib.load(scaler_pkl)
        model  = joblib.load(model_pkl)
        pipe = joblib.load(pipe_joblib)

        cls._artifacts = Artifacts()
        cls._artifacts.scaler = scaler
        cls._artifacts.model = model
        cls._artifacts.pipe = pipe
        return cls._artifacts