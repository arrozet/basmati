"""
Lambda handler para Auth Service
"""
from mangum import Mangum
from main import app

# Crear handler para AWS Lambda usando Mangum
handler = Mangum(app, lifespan="off")
