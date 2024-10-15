import numpy as np
from enum import Enum, auto
from pathlib import Path
import typing
from abc import ABC, abstractmethod
import joblib
import pickle

class Framework(Enum):
    SKLEARN = auto()

class Model(ABC):
    def __init__(self, model_name: str, model_path: typing.Union[str, Path], framework: Framework, classes: typing.List[str]):
        self.model_name = model_name
        self.model_path = Path(model_path)
        self.framework = framework
        self.classes = classes
        self.model = None
        self.load()

    def load(self):
        if not self.model_path.exists():
            raise ValueError(f"Model file {self.model_path} not found.")

        if self.framework == Framework.SKLEARN:
            self._load_sklearn_model()
        else:
            raise ValueError(f"Framework {self.framework} is not supported.")

    def _load_sklearn_model(self):
        """
        Load a sklearn model using joblib.
        """
        self.model = joblib.load(self.model_path)

    @abstractmethod
    def predict(self, X: typing.Any) -> typing.Any:
        pass

    def __call__(self, X: typing.Any) -> typing.Any:
        return self.predict(X)

class LinkScribeModel:
    def __init__(self, model_path):
        self.model_path = model_path
        self.model = self.load_model()

    def load_model(self):
        return joblib.load(self.model_path)  # Cargar el modelo usando joblib

    def predict(self, content):
        # Realiza la predicción y devuelve la categoría
        return self.model.predict([content])[0]  # Asegúrate de que el contenido sea una lista

