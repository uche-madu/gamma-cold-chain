# from fastapi import APIRouter, HTTPException, BackgroundTasks
# from app.services.call import generate_call_script, make_call
# from app.schemas.call import CallRequest, BulkCallRequest, BulkCallResponse

# router = APIRouter()

# @router.post("/call/single", response_model=str)
# async def single_call(request: CallRequest):
#     """
#     Generate a call script and make a single call.
#     """
#     try:
#         call_script = await generate_call_script(request.dict())
#         call_status = await make_call(request.prospect_phone, call_script.call_script)
#         return call_status
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @router.post("/call/bulk", response_model=BulkCallResponse)
# async def bulk_call(request: BulkCallRequest, background_tasks: BackgroundTasks):
#     """
#     Generate call scripts and initiate multiple calls asynchronously.
#     """
#     call_results = []

#     async def process_call(prospect):
#         try:
#             script = await generate_call_script(prospect.dict())
#             status = await make_call(prospect.prospect_phone, script.call_script)
#             call_results.append({"phone": prospect.prospect_phone, "status": status})
#         except Exception as e:
#             call_results.append({"phone": prospect.prospect_phone, "status": f"failed: {str(e)}"})

#     for prospect in request.prospects:
#         background_tasks.add_task(process_call, prospect)

#     return BulkCallResponse(results=call_results)
