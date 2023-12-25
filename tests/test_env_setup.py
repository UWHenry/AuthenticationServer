import sys
import os

# Add the parent directory to sys.path
current_dir = os.path.dirname(__file__)
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# set up environment variables
os.environ['DATABASE_URL'] = "sqlite:///test.db"
os.environ['CORS_ORIGINS'] = ""

import pytest
from main import app
from fastapi.testclient import TestClient

# pytest set up and tear down resources
@pytest.fixture
def client():
    client = TestClient(app)
    