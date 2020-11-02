class Config:
    DEBUG = False
    CSRF_ENABLED = True
    MONGO_URI = 'mongodb://127.0.0.1:27017/MyBookingServices'
    JWT_SECRET_KEY = 'SeCretPasSword9'
    DATABASE_CONNECT_OPTIONS = {}


class DevelopmentConfig(Config):
    ENV = "development"
    DEBUG = True
    TESTING = True


class StagingConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False


APP_CONFIG = {
    'development': DevelopmentConfig,
    'staging': StagingConfig,
    'production': ProductionConfig,
}
