import pandas as pd
from loguru import logger
from app.utils.process_files import read_file
from app.services.email import generate_email_content, send_email
from app.services.call import generate_call_script, make_call
from langchain.schema.runnable import RunnableBranch

async def extract_prospects(file_path):
    """
    Extracts and validates prospect data from a given file.

    Parameters:
        file_path (str): Path to the file.

    Returns:
        pd.DataFrame: DataFrame containing valid prospect data or None if errors occur.
    """
    df = read_file(file_path)
    if df is None:
        return None

    required_columns = {
        "email": ["prospect_email", "prospect_name", "company_name", "prospect_title", "industry", "engagement_level", "objections", "outreach_type", "sender_name", "sender_title", "insurance_company_name", "outreach_description"],
        "call": ["prospect_phone", "prospect_name", "company_name", "prospect_title", "industry", "engagement_level", "objections", "outreach_type", "sender_name", "sender_title", "insurance_company_name", "outreach_description"]
    }

    if "outreach_type" not in df.columns:
        logger.error("Missing required column: outreach_type.")
        return None
    
    valid_types = {"email", "call"}
    df = df[df["outreach_type"].isin(valid_types)]
    
    if df.empty:
        logger.error("No valid outreach type (email/call) found in the file.")
        return None

    for outreach_type in valid_types:
        missing_cols = [col for col in required_columns[outreach_type] if col not in df.columns]
        if missing_cols:
            logger.warning(f"Missing columns {missing_cols}. Some {outreach_type} rows may be skipped.")

    if "objections" in df.columns:
        df["objections"] = df["objections"].apply(lambda x: x.split(",") if isinstance(x, str) else [])

    logger.success(f"Successfully processed file: {file_path} with {len(df)} rows.")
    return df

async def process_outreach(file_path, output_file):
    """
    Processes outreach data (email or call) using LangChain's RunnableBranch.

    Parameters:
        file_path (str): Path to the file.
        output_file (str): Path to save the processed file.

    Returns:
        str: Path to the updated file.
    """
    df = await extract_prospects(file_path)
    if df is None:
        return None

    results = []

    async def handle_email(row):
        logger.info(f"Generating email for {row['company_name']}")
        response = generate_email_content(row)

        if not response or not response.subject:
            logger.warning(f"Email generation failed for {row['company_name']}")
            return row  # Return row unchanged

        logger.info(f"Generated email - Subject: {response.subject} for {row['company_name']}")

        row["subject"] = response.subject
        row["email"] = response.email
        row["engagement_advice"] = response.engagement_advice

        # Send the email
        logger.info(f"Sending email to {row['prospect_email']} for {row['company_name']}")
        send_status = await send_email(response)
        logger.critical(f"Sent email to {row['prospect_email']}")

        if send_status:
            logger.success(f"Email successfully sent to {row['prospect_email']} for {row['company_name']}")
        else:
            logger.error(f"Failed to send email to {row['prospect_email']} for {row['company_name']}")

        return row


    # async def handle_call(row):
    #     logger.info(f"Generating call script for {row['company_name']}")
    #     response = await generate_call_script(row)

    #     if not response or not response.call_script:
    #         logger.warning(f"Call script generation failed for {row['company_name']}")
    #         return row  # Return row unchanged

    #     logger.info(f"Generated call script for {row['company_name']}")

    #     row["call_script"] = response.call_script
    #     row["engagement_advice"] = response.engagement_advice

    #     # Make the call
    #     logger.info(f"Making call to {row['prospect_phone']} for {row['company_name']}")
    #     call_status = await make_call(row["prospect_phone"], response.call_script)
    #     logger.critical(f"make_call called with: {row["prospect_phone"]}, {response.call_script}")

    #     if call_status:
    #         logger.success(f"Call completed with status: {call_status} for {row['company_name']}")
    #     else:
    #         logger.error(f"Call failed for {row['company_name']}")

    #     row["call_status"] = call_status
    #     return row
    

    async def handle_call(row):
        logger.info(f"Generating call script for {row['company_name']}")
        response = await generate_call_script(row)

        if not response or not response.call_script:
            logger.warning(f"Call script generation failed for {row['company_name']}")
            return row  # Return row unchanged

        logger.info(f"Generated call script for {row['company_name']}")

        # Ensure the row is updated correctly
        updated_row = row.copy()
        updated_row["call_script"] = response.call_script
        updated_row["engagement_advice"] = response.engagement_advice

        # Make the call
        logger.info(f"Making call to {updated_row['prospect_phone']} for {updated_row['company_name']}")
        call_status = await make_call(updated_row["prospect_phone"], response.call_script)

        if call_status:
            logger.success(f"Call successfully placed to {row['prospect_phone']} for {row['company_name']}")
        else:
            logger.error(f"Failed to place call to {row['prospect_phone']} for {row['company_name']}")

        return updated_row



    branch = RunnableBranch(
        (lambda x: isinstance(x, dict) and x.get("outreach_type") == "email", handle_email),
        (lambda x: isinstance(x, dict) and x.get("outreach_type") == "call", handle_call),
        lambda x: x  # Default case (do nothing)
    )
    
    for _, row in df.iterrows():
        try:
            logger.info(f"Processing {row['outreach_type']} for {row['company_name']}")
            row_dict = row.to_dict()  # Convert Pandas Series to dictionary
            processed_row = await branch.ainvoke(row_dict)  # Pass mutable dict
            results.append(processed_row)  # Append updated row
        except Exception as e:
            logger.error(f"Error processing {row['outreach_type']} for {row['company_name']}: {e}")


    output_df = pd.DataFrame(results)
    output_df.to_csv(output_file, index=False)

    logger.success(f"Processing completed. File saved at {output_file}")
    return output_file
