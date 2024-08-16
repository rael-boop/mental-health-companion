# MHC: Mental Health Companion

MHC is a RESTful API application built using FastAPI and SQLAlchemy, designed to provide a robust and efficient backend solution for your projects.

## Prerequisites
- **Docker**: When running with docker, a docker installation is required, docker can be installed from [docker's official website](https://www.docker.com/products/docker-desktop/)
- **Python**: When running with bare python, a python installation is required, install python from [python's official website](https://www.python.org/downloads/)
- **CUDA GPU**: In order to load the chat model, a system with CUDA GPU is required, get [Nvidia toolkit](https://developer.nvidia.com/cuda-downloads)

## Features

- **FastAPI**: MHC leverages the power of FastAPI, a modern, high-performance web framework for building APIs with Python.
- **SQLAlchemy**: The application uses SQLAlchemy as the Object-Relational Mapping (ORM) library, allowing seamless interaction with relational databases.
- **Asynchronous**: MHC supports asynchronous request handling, enabling efficient use of resources and improved performance.
- **Data Validation**: FastAPI's built-in data validation ensures that incoming data adheres to predefined schemas, reducing errors and improving reliability.
- **Automatic Documentation**: MHC automatically generates interactive API documentation using Swagger UI, making it easy to explore and test the available endpoints.

## Installation

1. Navigate to the project directory:

```bash
cd mhc
```

2. Create a virtual environment (optional but recommended):

```bash
python -m virtualenv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

3. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Configuration

MHC uses environment variables for configuration. Create a `.env` file in the project root, copy the contents of .env.example and set values appropriately

## Usage

### Using Python

#### Development 
1. Start the application:

```bash
python main.py
```

2. Open your web browser and navigate to `http://localhost:8000/docs` to access the interactive Swagger UI documentation.

3. Explore the available endpoints, send requests, and interact with the API.

#### Production 
1. Start the application:
- The production server uses a combination of gunicorn with uvicorn

```bash
gunicorn "main:setup()" --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:${PORT} --timeout 90
```
The setup function is called first to create the tables appropriately in the database

### Using Docker  (Production|Development)
Start by visiting [docker website](https://docs.docker.com/get-docker/) to install docker for your OS, once the installation is complete 
 
1. Build the application:
```sh
docker-compose -f gpu-docker-compose.yml --env-file .env build
```

2. Start the the application:
```sh 
docker-compose -f gpu-docker-compose.yml --env-file .env up
```

## Acknowledgments

MHC was built using the following open-source libraries and tools:

- [FastAPI](https://fastapi.tiangolo.com/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [Uvicorn](https://www.uvicorn.org/)
- [Pydantic](https://pydantic-docs.helpmanual.io/)