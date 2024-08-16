from fastapi import APIRouter
from pydantic import BaseModel

from src.models.faq import Faq, FaqSchema
from src.models import DatabaseSession
from src.middlewares.auth import AdminUser

from src.utils import AppUtils


faqs_router = APIRouter(
    prefix="/faqs", tags=['faqs']
)


class FaqCreateInput(BaseModel):
    question: str
    answer: str


@faqs_router.post("/")
def create_faq(user: AdminUser, body: FaqCreateInput):
    with DatabaseSession().withSession() as session:
        faq_orm = Faq(
            question=body.question,
            answer=body.answer
        )

        session.add(faq_orm)
        session.commit()

        faq = FaqSchema.from_orm(faq_orm)

        return AppUtils.create_response(
            message="Faq Created successfully",
            data={
                "faq": faq.model_dump()
            }
        )


@faqs_router.get("/")
def list_faq():
    with DatabaseSession().withSession() as session:
        faq_orm = session.query(Faq).all()
        faqs = [
            FaqSchema.from_orm(faq_orm_item).model_dump()
            for faq_orm_item in faq_orm
        ]

        return AppUtils.create_response(
            message="Faqs list",
            data={
                "faqs": faqs
            }
        )
