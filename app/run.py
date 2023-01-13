from .main import create_app
from .settings import Settings

settings = Settings()
app = create_app(settings)
