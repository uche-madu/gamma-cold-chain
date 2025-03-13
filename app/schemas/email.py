from pydantic import EmailStr, BaseModel, Field
from typing import List, Optional

class Prospect(BaseModel):
    prospect_email: EmailStr = Field(..., description="The email address of the prospect.")
    prospect_phone: Optional[str] = Field(None, description="The phone number of the prospect.")
    prospect_name: str = Field(..., description="The name of the prospect.")
    company_name: str = Field(..., description="The name of the prospect's company.")
    prospect_title: Optional[str] = Field(None, description="The title of the prospect at their company.")
    industry: str = Field(..., description="The industry in which the prospect's company operates.")
    engagement_level: int = Field(..., description="The previous engagement level (a score from 1 to 10).")
    objections: Optional[List[str]] = Field(None, description="A potential objection raised by the prospect.")

class EmailRequest(BaseModel):
    prospect_info: Prospect = Field(..., description="An object containing all prospect details.")
    outreach_description: str = Field(..., description="A description of the outreach strategy to be incorporated into the email.")
    insurance_company_name: str = Field(..., description="The name of the insurance company sending the email.")
    sender_name: Optional[str] = Field(None, description="The name of the sender.")
    sender_title: Optional[str] = Field("", description="The title of the sender at the insurance company.")

class EmailResponse(BaseModel):
    prospect_email: EmailStr = Field(..., description="The email address of the prospect, as provided in the input.")
    subject: str = Field(..., description="A compelling email subject line generated by the LLM.")
    email: str = Field(..., description="""A **personalized cold email** that follows this structure:  
   - **[Opening sentence]**: Connect with their industry, a recent trend, or challenge.  
   - **[Value proposition]**: Explain how your insurance solution helps companies in their industry.  
   - **[Objection handling]**: Address a common concern relevant to their industry.  
   - **[CTA]**: Suggest a **quick call, demo, or free consultation**. """)
    engagement_advice: str = Field(..., description="A **follow-up strategy** and recommendations to keep the client engaged based on their industry and potential objections.")
    
    