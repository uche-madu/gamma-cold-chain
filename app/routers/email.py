from fastapi import APIRouter, BackgroundTasks, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
import pandas as pd
from app.schemas.email import EmailRequest
from app.services.email import generate_email_content, send_email
from loguru import logger

router = APIRouter(prefix="/email", tags=["Email"])

@router.post("/")
async def generate_and_send_email(email_request: EmailRequest, background_tasks: BackgroundTasks) -> JSONResponse:
    
    params = {
        "prospect_email": email_request.prospect_info.prospect_email,
        "prospect_name": email_request.prospect_info.prospect_name,
        "company_name": email_request.prospect_info.company_name,
        "prospect_title": email_request.prospect_info.prospect_title,
        "industry": email_request.prospect_info.industry,
        "engagement_level": email_request.prospect_info.engagement_level,
        "objections": email_request.prospect_info.objections,
        "outreach_description": email_request.outreach_description,
        "insurance_company_name": email_request.insurance_company_name,
        "sender_name": email_request.sender_name,
        "sender_title": email_request.sender_title,
    }
    
    try:
        response = generate_email_content(params)

        # Schedule sending the email as a background task.
        background_tasks.add_task(send_email, response)
    except Exception as e:
        logger.error(f"Error generating email for {email_request.prospect_info.company_name}'s {email_request.prospect_info.prospect_email}: {e}")
        raise HTTPException(status_code=500, detail="Email generation failed.")

    return JSONResponse(
        status_code=200, 
        content={"status": "success", "results": jsonable_encoder(response)})


@router.post("/bulk")
async def generate_and_send_bulk_email(background_tasks: BackgroundTasks, file: UploadFile = File(...)) -> JSONResponse:
    try:
        # Read input file (CSV assumed)
        df = pd.read_csv(file.file)

        # Ensure required columns are present
        required_columns = [
            "prospect_email", "prospect_name", "company_name", "prospect_title",
            "industry", "engagement_level", "objections", "outreach_description",
            "insurance_company_name", "sender_name", "sender_title", "outreach_type"
        ]

        missing_cols = [col for col in required_columns if col not in df.columns]
        if missing_cols:
            return JSONResponse(status_code=400, content={"error": f"Missing columns: {missing_cols}"})

        results = []

        for _, row in df.iterrows():
            params = {
                "prospect_email": row["prospect_email"],
                "prospect_name": row["prospect_name"],
                "company_name": row["company_name"],
                "prospect_title": row["prospect_title"],
                "industry": row["industry"],
                "engagement_level": row["engagement_level"],
                "objections": row["objections"],
                "outreach_description": row["outreach_description"],
                "insurance_company_name": row["insurance_company_name"],
                "sender_name": row["sender_name"],
                "sender_title": row["sender_title"],
            }

            try:
                response = generate_email_content(params)
                background_tasks.add_task(send_email, response)

                # Append results
                row["subject"] = response.subject
                row["email"] = response.email
                row["engagement_advice"] = response.engagement_advice
                results.append(row)

            except Exception as e:
                logger.error(f"Error generating email for {row['company_name']}: {e}")

        # Convert results back to DataFrame and save
        output_df = pd.DataFrame(results)
        output_file = "processed_outreach_results.csv"
        output_df.to_csv(output_file, index=False)

        return JSONResponse(status_code=200, content={"status": "success", "message": "Emails generated and sent successfully", "file": output_file})

    except Exception as e:
        logger.error(f"Bulk email processing failed: {e}")
        raise HTTPException(status_code=500, detail="Bulk email processing failed.")