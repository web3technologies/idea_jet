from idea_jet.settings.settings import *

DEBUG = False

CORS_ORIGIN_WHITELIST = [
    "https://app.ideajet.ai"
]

# DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

# # AWS S3 specific settings
# AWS_ACCESS_KEY_ID = 'your-access-key-id'
# AWS_SECRET_ACCESS_KEY = 'your-secret-access-key'
# AWS_STORAGE_BUCKET_NAME = 'your-bucket-name'
# AWS_S3_REGION_NAME = 'your-region-name'