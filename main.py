from src.scripts.models import create_tables
from src.utils.logger import logger
from src.routes import routes
from fastapi import FastAPI
from fastapi_pagination import add_pagination

app = FastAPI()


@app.get("/")
def ping():
    logger.debug("::> Server Health check")
    return "MHC SERVICE HEALTHY"


app.include_router(routes)


def setup():
    create_tables()
    return app


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )


add_pagination(app)
