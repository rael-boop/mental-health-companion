from fastapi import APIRouter, File, UploadFile, Form
from fastapi_pagination.customization import CustomizedPage, UseFieldsAliases
from fastapi_pagination import Page, paginate
from pydantic import BaseModel
from src.config import Config
from typing import Annotated
from fastapi import status

from src.models.resource import Resource
from src.schemas.resource import ResourceSchema
from src.models import DatabaseSession
from src.middlewares.auth import AdminUser
from src.utils import AppUtils
import cloudinary
import cloudinary.uploader

cloudinary.config(
    cloud_name=Config.CLOUDINARY_CLOUD_NAME,
    api_key=Config.CLOUDINARY_API_KEY,
    api_secret=Config.CLOUDINARY_API_SECRET,
)

resources_router = APIRouter(prefix="/resource", tags=['resource'])


PaginationPage = CustomizedPage[
    Page,
    UseFieldsAliases(items="data")
]


@resources_router.get("/resources")
def list_resources() -> PaginationPage[ResourceSchema]:
    with DatabaseSession().withSession() as session:
        resources_orm = session.query(Resource).all()
        resources = [ResourceSchema.from_orm(resource_orm)
                     for resource_orm in resources_orm]
        resources.reverse()
        return paginate(resources)


class ResourceDataInput(BaseModel):
    title: str
    video_url: str
    description: str


@resources_router.post("/resources")
def create_resource(
    user: AdminUser,
    title: Annotated[str, Form()],
    video_url:  Annotated[str, Form()],
    description:  Annotated[str, Form()],
    thumbnail: UploadFile = File(...),
):
    with DatabaseSession().withSession() as session:
        result = cloudinary.uploader.upload(thumbnail.file)
        thumbnail_url = result.get("url")
        resource_orm = Resource(
            title=title,
            video_url=video_url,
            description=description,
            thumbnail_url=thumbnail_url
        )
        session.add(resource_orm)
        session.commit()

        resource = ResourceSchema.from_orm(resource_orm)
        return AppUtils.create_response(
            message="Resources",
            data=resource
        )
