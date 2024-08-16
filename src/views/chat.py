from fastapi import APIRouter, status, Query
from sqlalchemy.exc import NoResultFound
from pydantic import BaseModel
from fastapi_pagination import Page, paginate
from fastapi_pagination.customization import CustomizedPage, UseFieldsAliases
from datetime import datetime, timedelta

from src.utils import AppUtils, CustomError
from src.utils.logger import logger
from src.middlewares.auth import ActiveUser
from src.models import text_classifier, device, tokenizer, generator
from src.models.user import User
from src.models.chat import Chat, Prompt, Sentiment
from src.schemas.chat import ChatSchema, PromptSchema, SentimentSchema
from src.models import DatabaseSession


chat_route = APIRouter(
    prefix="/chat",
    tags=['chat']
)


PaginationPage = CustomizedPage[
    Page,
    UseFieldsAliases(items="data")
]


class PromptInput(BaseModel):
    chat_id: int = None
    prompt: str


def _generateResponse(messages) -> str:
    if generator is not None:
        # Tokenize inputs
        input_ids = tokenizer.apply_chat_template(
            conversation=messages,
            tokenize=True,
            add_generation_prompt=True,
            return_tensors='pt').to(device)

        # Get output ids with dynamic stopping criterion
        max_tokens = 150  # Define maximum tokens for the response
        min_length = 20  # Define minimum length for the response

        # get out put ids
        output_ids = generator.generate(
            max_length=max_tokens + input_ids.shape[-1],
            min_length=min_length + input_ids.shape[-1],
            input_ids=input_ids,
            do_sample=True,
            pad_token_id=2,
        )

        # Response
        response = tokenizer.batch_decode(
            output_ids.detach().cpu().numpy(),
            skip_special_tokens=True
        )

        # Extract message
        generated_response = response[0].split("[/INST]")
        generated_response = generated_response[1]

        # cut response to return response withing last fullstop index
        last_full_stop_index = generated_response.rfind(".")
        if last_full_stop_index != -1:
            generated_response = generated_response[:last_full_stop_index + 1]
    else:
        logger.error("::> CUDA GPU is required")
        generated_response = "Generator requires a CUDA GPU to run,\
switch to os with CUDA GPU and try again"

    return generated_response


@chat_route.post("/prompt")
def prompt(user: ActiveUser, body: PromptInput):

    # Retrieve first 3 sentiments
    generated_sentiments = text_classifier([body.prompt])[0][:3]
    # Perform DB functions
    with DatabaseSession().withSession() as session:
        # Create chat
        chat_orm = None
        if body.chat_id is not None:
            try:
                chat_orm = session.query(Chat).where(
                    Chat.id == body.chat_id, Chat.owner_id == user.id).one()
            except NoResultFound:
                raise CustomError(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No Chat found",
                )
        else:
            chat_orm = Chat(
                title=body.prompt[:40],
                owner_id=user.id
            )
            session.add(chat_orm)
            session.commit()

        if chat_orm is None:
            raise CustomError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while trying to retrieve chat,\
                    please try again"
            )

        prompts = session.query(Prompt).where(Prompt.chat_id == chat_orm.id)
        prompts = prompts[:5]

        messages = []
        messages.append({
            "role": "user",
            "content": body.prompt
        })

        generated_response = _generateResponse(messages)

        # Create prompt
        prompt_orm = Prompt(
            chat_id=chat_orm.id,
            bot_response=generated_response,
            prompt=body.prompt
        )
        session.add(prompt_orm)
        session.commit()

        chat = ChatSchema.from_orm(chat_orm)
        prompt = PromptSchema.from_orm(prompt_orm)
        sentiments = []

        # Create sentiments
        for sentiment in generated_sentiments:
            # Greater than 30%
            if sentiment['score'] > 0.3:
                sentiment_orm = Sentiment(
                    prompt_id=prompt_orm.id,
                    score=sentiment['score'],
                    sentiment=sentiment['label']
                )
                session.add(sentiment_orm)
                session.commit()

                sentiments.append(
                    SentimentSchema.from_orm(sentiment_orm).model_dump()
                )

        # Create Response
        return AppUtils.create_response(
            message="Prompt response",
            data={
                "chat": chat.model_dump(),
                "prompt": prompt.model_dump(),
                "sentiments": sentiments
            }
        )


@chat_route.get("/chats")
def chats(user: ActiveUser) -> PaginationPage[ChatSchema]:
    with DatabaseSession().withSession() as session:
        chats_orm = session.query(Chat).where(
            Chat.owner_id == user.id
        )
        chats = [ChatSchema.from_orm(chat_orm)
                 for chat_orm in chats_orm]
        chats.reverse()
        return paginate(chats)


@chat_route.get("/prompts/{chat_id}")
def list_prompts(user: ActiveUser, chat_id: int) -> Page[PromptSchema]:
    with DatabaseSession().withSession() as session:
        # ensure user owns chat
        try:
            chat = session.query(Chat).where(
                Chat.id == chat_id, Chat.owner_id == user.id).one_or_none()
            if not chat:
                raise CustomError(
                    detail="Chat does not exists for user",
                    status_code=status.HTTP_404_NOT_FOUND
                )
        except NoResultFound:
            raise CustomError(
                detail="Chat does not exists for user",
                status_code=status.HTTP_404_NOT_FOUND
            )

        # return prompts
        prompts_orm = session.query(Prompt).where(Prompt.chat_id == chat_id)
        prompts = [PromptSchema.from_orm(prompt_orm)
                   for prompt_orm in prompts_orm]
        prompts.reverse()
        return paginate(prompts)


@chat_route.get("/sentiments")
def historical_sentiments(
    user: ActiveUser,
        start_date: datetime = Query(
            default=(datetime.utcnow() - timedelta(days=30)),
            description="Start date for sentiment analysis (YYYY-MM-DD format)"
        ),
        end_date: datetime = Query(
            default=datetime.utcnow(),
            description="End date for sentiment analysis (YYYY-MM-DD format)"
        )
):
    with DatabaseSession().withSession() as session:
        current_date = datetime.utcnow()

        # ensure end date is not greater than current date
        if end_date > current_date:
            raise CustomError(
                detail="End date range exceeded current day and time",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        # ensure start date is less than end date
        if start_date > end_date:
            raise CustomError(
                detail="Start date range should be less than end date",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        # query chat sentiment belonging to user \
            # Sentiment.Prompt.Chat.owner_id == user.id
        sentiments_orm = session.query(Sentiment)\
            .join(Sentiment.prompt)\
            .join(Prompt.chat)\
            .join(Chat.owner)\
            .where(User.id == user.id)\
            .where(Sentiment.created_at >= start_date)\
            .where(Sentiment.created_at <= end_date).all()

        sentiments = [
            SentimentSchema.from_orm(sentiment_orm).model_dump()
            for sentiment_orm in sentiments_orm
        ]

        return AppUtils.create_response(
            message="Sentiment historical data",
            data=sentiments
        )
