from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnableBranch, RunnableParallel
from langchain_core.output_parsers import JsonOutputParser

from fastapi_mail import FastMail, ConnectionConfig, MessageSchema, MessageType
from loguru import logger

from app.core.settings import settings
from app.core.config import llama3_70b_llm
from app.schemas.email import EmailResponse

conf = ConnectionConfig(
    MAIL_USERNAME=settings.mail_username,
    MAIL_PASSWORD=settings.mail_password,
    MAIL_FROM=settings.mail_from,
    MAIL_PORT=settings.mail_port,
    MAIL_SERVER=settings.mail_server,
    MAIL_FROM_NAME=settings.mail_from_name,
    MAIL_STARTTLS=settings.mail_starttls,
    MAIL_SSL_TLS=settings.mail_ssl_tls,
    USE_CREDENTIALS=settings.use_credentials,
    VALIDATE_CERTS=settings.validate_certs
)

fast_mail = FastMail(conf)


prompt = """
You are an AI-powered Cold Outreach Assistant for an insurance company specializing in personalized marketing. Your goal is to craft **highly engaging cold emails** tailored to the input provided. Output only the email content following the provided format. Do not include any extra commentary or explanation.

---

Input: 
- **Prospect's Email**: {prospect_email}  
- **Prospect's name**: {prospect_name}  
- **Prospect's Company Name**: {company_name}  
- **Prospect's Title at company**: {prospect_title}  
- **Industry**: {industry}  
- **Previous Engagement Level**: {engagement_level}  
- **Potential Objections**: {objections}  
- **Outreach Description**: {outreach_description}  
- **Industry Focus**: {industry_focus}  
- **Sender's Company Name**: {insurance_company_name}  
- **Sender's Name**: {sender_name}  
- **Sender's Title at Company**: {sender_title}  

---

###Note: The email is sent to {prospect_name} whose title at {company_name} is {prospect_title} (if provided). So tailor the email accordingly.

### **Output Format (Strict JSON)**
{{
  "prospect_email": "{prospect_email}",
  "subject": "[Compelling subject line]",
  "email": "[Generated cold email]",
  "engagement_advice": "[Follow-up strategy and recommendations]"
}}
"""

# Define Industry-Specific Messaging
def get_industry_focus(industry: str) -> str:
    industry = industry.lower()
    industry_focus_map = {
        "tech": "emphasize innovation and cutting-edge technology solutions.",
        "finance": "highlight security and robust ROI potential.",
        "healthcare": "stress compliance and efficiency.",
    }
    return industry_focus_map.get(industry, "highlight tailored benefits.")

# Define JSON Parser
parser = JsonOutputParser(pydantic_object=EmailResponse)

prompt_template = PromptTemplate(
    template=prompt,
    input_variables=[
        "prospect_email",
        "prospect_name",
        "company_name",
        "prospect_title",
        "industry",
        "industry_focus",
        "engagement_level",
        "objections",
        "outreach_description",
        "insurance_company_name",
        "sender_name",
        "sender_title"
    ],
    partial_variables={"format_instructions": parser.get_format_instructions()}
)

def generate_email_content(params: dict) -> EmailResponse:
    logger.info(f"Generating email content for: {params.get('prospect_email')}")
    
    params["industry_focus"] = get_industry_focus(params["industry"])
    chain = prompt_template | llama3_70b_llm | parser

    try:
        response_dict = chain.invoke(params)
        logger.success(f"Email content generated: {response_dict}")
    except Exception as e:
        logger.error(f"Error generating email content: {e}")
        raise e

    return EmailResponse.model_validate(response_dict)


async def send_email(response: EmailResponse) -> None:
    logger.info(f"Attempting to send email to {response.prospect_email}")

    message = MessageSchema(
        subject=response.subject,
        recipients=[response.prospect_email],
        body=response.email,
        subtype=MessageType.plain,
    )

    fm = FastMail(conf)

    try:
        await fm.send_message(message)
        logger.success(f"Email successfully sent to {response.prospect_email}")
    except Exception as e:
        logger.error(f"Failed to send email to {response.prospect_email}: {e}")
