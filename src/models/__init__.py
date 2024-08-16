from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from transformers import pipeline
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftConfig, PeftModel
import torch

from src.config import Config


class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(primary_key=True)


engine = create_engine(Config.DATABASE_URI, echo=True)


class DatabaseSession:
    def withSession(self):
        class SessionContextManager:
            def __enter__(self):
                self.session = Session(engine)
                return self.session

            def __exit__(self, exc_type, exc_value, traceback):
                if exc_type:
                    self.session.rollback()
                else:
                    self.session.commit()
                self.session.close()

        return SessionContextManager()


text_classifier = pipeline(
    task="text-classification",
    model=Config.SENTIMENT_MODEL, top_k=None
)
base_model = "mistralai/Mistral-7B-Instruct-v0.2"
adapter = "GRMenon/mental-health-mistral-7b-instructv0.2-finetuned-V2"

# Load tokenizer
tokenizer = AutoTokenizer.from_pretrained(
    base_model,
    add_bos_token=True,
    trust_remote_code=True,
    padding_side='left'
)

# Create peft model using base_model and finetuned adapter
config = PeftConfig.from_pretrained(adapter)
generator = None
device = "cuda" if torch.cuda.is_available() else "cpu"

try:
    model = AutoModelForCausalLM.from_pretrained(
        base_model,
        load_in_4bit=True,
        device_map='auto',
        torch_dtype='auto'
    )
    generator = PeftModel.from_pretrained(model, adapter)
    generator.to(device)
    generator.eval()
except Exception as E:
    print("FAILED TO RUN MODEL", E)
    pass
