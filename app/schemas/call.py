from pydantic import BaseModel, Field
from typing import List, Optional

class CallRequest(BaseModel):
    """
    Schema for initiating a cold call script generation request.
    """
    prospect_phone: str = Field(..., description="The phone number of the prospect to be called, in international format (+1234567890).")
    prospect_name: str = Field(..., description="The full name of the prospect receiving the call.")
    company_name: str = Field(..., description="The name of the company the prospect works for.")
    prospect_title: Optional[str] = Field(None, description="The job title of the prospect at their company (e.g., 'Marketing Director').")
    industry: str = Field(..., description="The industry the prospect's company operates in (e.g., 'Finance', 'Tech', 'Healthcare').")
    engagement_level: int = Field(..., ge=0, lt=5, description="The previous engagement level (a score from 0 to 4).")
    objections: Optional[List[str]] = Field(None, description="Potential objections the prospect might have (e.g., 'Budget concerns', 'Already using a competitor').")
    outreach_description: str = Field(..., description="A brief description of the purpose of the call and key selling points.")
    insurance_company_name: str = Field(..., description="The name of the insurance company initiating the outreach.")
    sender_name: str = Field(..., description="The full name of the sales representative or agent making the call.")
    sender_title: str = Field(..., description="The job title of the sender at the insurance company (e.g., 'Senior Sales Executive').")

class CallResponse(BaseModel):
    """
    Schema for the AI-generated cold call script response.
    """
    prospect_phone: str = Field(..., description="The phone number of the prospect being called.")
    call_script: str = Field(..., description="The AI-generated engaging cold call script to be used during the call.")
    engagement_advice: str = Field(..., description="A **follow-up strategy** and recommendations to keep the client engaged.")
    call_status: Optional[str] = Field(None, description="The status of the call after execution (e.g., 'queued', 'completed', 'failed').")
