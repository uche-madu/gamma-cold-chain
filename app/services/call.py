from typing import Dict

from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from loguru import logger
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse

from app.core.settings import settings
from app.core.config import llama3_70b_llm
from app.schemas.call import CallResponse
from app.services.email import get_industry_focus 

TWILIO_ACCOUNT_SID = settings.twilio_account_sid.get_secret_value()
TWILIO_AUTH_TOKEN = settings.twilio_auth_token.get_secret_value()
TWILIO_PHONE_NUMBER = settings.twilio_phone_number
TWILIO_VERIFIED_PHONE_NUMBER = settings.twilio_verified_phone_number


# Initialize Twilio client
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Call Script Generation Prompt
call_prompt = """
You are an AI-powered Cold Call Assistant for an insurance company. Your task is to generate **highly persuasive call scripts** for cold outreach based on the input. Ensure the script is natural and engaging.

---
Input:
**Prospect Details:**  
- **Prospect's Name:** {prospect_name}  
- **Company Name:** {company_name}  
- **Prospect's Title:** {prospect_title}  
- **Industry:** {industry}  
- **Previous Engagement Level:** {engagement_level}  
- **Potential Objections:** {objections}  
- **Outreach Description:** {outreach_description}  
- **Industry Focus:** {industry_focus}  
- **Sender's Company Name:** {insurance_company_name}  

---

### **Call Script Format (Strict JSON)**
{{
  "prospect_phone": "{prospect_phone}",
  "call_script": "[Generated cold call script]",
  "engagement_advice": "[Follow-up strategy and recommendations]"
}}
"""

# JSON Parser
parser = JsonOutputParser(pydantic_object=CallResponse)

call_prompt_template = PromptTemplate(
    template=call_prompt,
    input_variables=[
        "prospect_phone",
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

async def generate_call_script(params: Dict) -> CallResponse:
    """
    Generate a cold call script using LangChain.
    """
    # Compute industry focus and add to parameters
    params["industry_focus"] = get_industry_focus(params["industry"])

    # Execute prompt chain
    chain = call_prompt_template | llama3_70b_llm | parser
    response_dict = await chain.ainvoke(params)

    return CallResponse.model_validate(response_dict)

async def make_call(phone_number: str, script: str):
    """
    Initiates a call to the prospect using Twilio.

    Parameters:
        phone_number (str): The prospect's phone number.
        script (str): The call script to be read.

    Returns:
        str: Call status (e.g., 'completed', 'failed').
    """

    twiml_response = VoiceResponse()
    twiml_response.say(script, voice='alice')

    try:
        call = client.calls.create(
            to=phone_number,
            from_=TWILIO_PHONE_NUMBER,
            twiml=twiml_response.to_xml()
        )

        logger.info(f"Call initiated to {phone_number}. Call SID: {call.sid}")
        return call.status  # Status: queued, ringing, in-progress, completed, failed

    except Exception as e:
        logger.error(f"Failed to initiate call to {phone_number}: {e}")
        raise e
