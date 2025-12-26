"""
Lambda handler usando Mangum.
"""
from mangum import Mangum
from main import app

# Handler para AWS Lambda
handler = Mangum(app, lifespan="off")
