import pytest
from app import create_app
from configuration.test_config import TestConfig  # TEST CONFIG

@pytest.fixture(scope='function')
def app():
    """Create app with test configuration"""
    app = create_app(TestConfig)  # USES TEST CONFIG
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()
    
    return app