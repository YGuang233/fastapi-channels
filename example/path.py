import os
from pathlib import Path

BasePath = Path(__file__).resolve().parent
TemplatePath: str = os.path.join(BasePath, "templates")
