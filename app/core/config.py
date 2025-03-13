from langchain.chat_models import init_chat_model
from .settings import settings

# Groq model initialization
ds_r1_llama_70b_llm = init_chat_model( 
    model="deepseek-r1-distill-llama-70b", 
    model_provider="groq",
    temperature=0.5,
    api_key=settings.GROQ_API_KEY
)

ds_r1_qwen_32b_llm = init_chat_model( 
    model="deepseek-r1-distill-qwen-32b", 
    model_provider="groq",
    temperature=0.5,
    api_key=settings.GROQ_API_KEY
)

llama3_70b_llm = init_chat_model( 
    model="llama3-70b-8192", 
    model_provider="groq",
    temperature=0.5,
    api_key=settings.GROQ_API_KEY
)

