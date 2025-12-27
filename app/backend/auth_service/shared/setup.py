"""Setup para el paquete compartido de Basmati"""
from setuptools import setup, find_packages

setup(
    name="basmati-shared",
    version="1.0.0",
    description="Lógica compartida entre microservicios de Basmati",
    packages=find_packages(),
    install_requires=[
        "pydantic-settings",
        "motor",
    ],
    python_requires=">=3.11",
)
