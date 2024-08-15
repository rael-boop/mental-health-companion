# MHC: Mental Health Companion

MHC is a RESTful API application built using FastAPI and SQLAlchemy, designed to provide a robust and efficient backend solution for your projects.

## Features

- **FastAPI**: MHC leverages the power of FastAPI, a modern, high-performance web framework for building APIs with Python.
- **SQLAlchemy**: The application uses SQLAlchemy as the Object-Relational Mapping (ORM) library, allowing seamless interaction with relational databases.
- **Asynchronous**: MHC supports asynchronous request handling, enabling efficient use of resources and improved performance.
- **Data Validation**: FastAPI's built-in data validation ensures that incoming data adheres to predefined schemas, reducing errors and improving reliability.
- **Automatic Documentation**: MHC automatically generates interactive API documentation using Swagger UI, making it easy to explore and test the available endpoints.

## Installation

1. Clone the repository:

```bash
git clone http:clone_url.git
```

2. Navigate to the project directory:

```bash
cd mhc
```

3. Create a virtual environment (optional but recommended):

```bash
python -m virtualenv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

4. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Configuration

MHC uses environment variables for configuration. Create a `.env` file in the project root, copy the contents of .env.example and set values appropriately

## Usage

### Development 

#### Using Python
1. Start the application:

```bash
python main.py
```

2. Open your web browser and navigate to `http://localhost:8000/docs` to access the interactive Swagger UI documentation.

3. Explore the available endpoints, send requests, and interact with the API.

#### Using Docker 
Start by visiting [docker website](https://docs.docker.com/get-docker/) to install docker for your OS, once the installation is complete 
 
1. Build the application:
```sh
docker-compose -f docker-compose.yml --env-file .env build
```

2. Start the the application:
```sh 
docker-compose -f docker-compose.yml --env-file .env up
```
### Production 
1. Start the application:
- The production server uses a combination of gunicorn with uvicorn

```bash
gunicorn "main:setup()" --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:${PORT} --timeout 90
```
The setup function is called first to create the tables appropriately in the database

## Contributing

Contributions to MHC are welcome! Please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Make your changes and commit them with descriptive commit messages.
4. Push your changes to your forked repository.
5. Submit a pull request to the main repository.

## License

MHC is released under the [MIT License](https://opensource.org/licenses/MIT).

## Acknowledgments

MHC was built using the following open-source libraries and tools:

- [FastAPI](https://fastapi.tiangolo.com/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [Uvicorn](https://www.uvicorn.org/)
- [Pydantic](https://pydantic-docs.helpmanual.io/)
