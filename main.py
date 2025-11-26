"""
Jess Voice Agent - FastAPI Backend
Provides tool endpoints for ElevenLabs conversational AI agent.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, timedelta
from database import get_supabase_client
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Jess Voice Agent API",
    description="Backend tools for autonomous debt collection voice agent",
    version="1.0.0"
)

# Configure CORS to allow ElevenLabs to call our endpoints
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify ElevenLabs domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Supabase client
supabase = get_supabase_client()


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class GetCaseDetailsRequest(BaseModel):
    phone: str = Field(..., description="Customer phone number")


class GetCaseDetailsResponse(BaseModel):
    debt_amount: float = Field(..., description="Total debt amount")
    due_date: str = Field(..., description="Original due date")
    risk_level: str = Field(..., description="Risk level: low, medium, high")
    days_overdue: int = Field(..., description="Number of days past due date")


class ProposePaymentPlanRequest(BaseModel):
    phone: str = Field(..., description="Customer phone number")
    installments: Optional[int] = Field(None, description="Number of installments requested")
    offer_amount: Optional[float] = Field(None, description="Settlement offer amount")


class ProposePaymentPlanResponse(BaseModel):
    plan_type: str = Field(..., description="Type of plan: installments or settlement")
    installment_amount: Optional[float] = Field(None, description="Amount per installment")
    payment_dates: Optional[List[str]] = Field(None, description="List of payment dates")
    total_amount: float = Field(..., description="Total amount to be paid")
    discount_applied: float = Field(..., description="Discount amount if applicable")
    accepted: bool = Field(..., description="Whether the plan is acceptable")
    message: str = Field(..., description="Explanation message")


class UpdateStatusRequest(BaseModel):
    phone: str = Field(..., description="Customer phone number")
    new_status: str = Field(..., description="New status: promised_to_pay, wrong_number, refused, etc.")
    summary: Optional[str] = Field(None, description="Summary of the interaction")


class UpdateStatusResponse(BaseModel):
    success: bool = Field(..., description="Whether the update was successful")
    message: str = Field(..., description="Status message")


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def calculate_days_overdue(due_date_str: str) -> int:
    """Calculate number of days overdue from a date string."""
    try:
        due_date = datetime.strptime(due_date_str, "%Y-%m-%d")
        today = datetime.now()
        delta = today - due_date
        return max(0, delta.days)
    except Exception as e:
        logger.error(f"Error calculating days overdue: {e}")
        return 0


def generate_payment_dates(num_installments: int) -> List[str]:
    """Generate monthly payment dates starting from next month."""
    dates = []
    base_date = datetime.now()
    
    for i in range(num_installments):
        # Add months (approximately 30 days each)
        payment_date = base_date + timedelta(days=30 * (i + 1))
        dates.append(payment_date.strftime("%Y-%m-%d"))
    
    return dates


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Jess Voice Agent API",
        "timestamp": datetime.now().isoformat()
    }


@app.post("/tools/get-case-details", response_model=GetCaseDetailsResponse)
async def get_case_details(request: GetCaseDetailsRequest):
    """
    Retrieve customer debt details.
    
    IMPORTANT: This should ONLY be called AFTER verbal identity confirmation.
    Jess must confirm she's speaking with the correct person before accessing
    sensitive debt information.
    """
    logger.info(f"🔍 Getting case details for phone: {request.phone}")
    
    try:
        # Query customer from database
        result = supabase.table('customers').select("*").eq('phone', request.phone).execute()
        
        if not result.data or len(result.data) == 0:
            logger.warning(f"⚠️  Customer not found: {request.phone}")
            raise HTTPException(status_code=404, detail="Customer not found")
        
        customer = result.data[0]
        
        # Calculate days overdue
        days_overdue = calculate_days_overdue(customer['due_date'])
        
        response = GetCaseDetailsResponse(
            debt_amount=float(customer['debt_amount']),
            due_date=customer['due_date'],
            risk_level=customer['risk_level'],
            days_overdue=days_overdue
        )
        
        logger.info(f"✅ Case details retrieved: ${response.debt_amount}, {days_overdue} days overdue")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error retrieving case details: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/tools/propose-payment-plan", response_model=ProposePaymentPlanResponse)
async def propose_payment_plan(request: ProposePaymentPlanRequest):
    """
    Calculate and validate payment plans or settlement offers.
    
    Supports two modes:
    1. Installment plan: Customer wants to pay in multiple installments
    2. Settlement offer: Customer offers a reduced amount
    """
    logger.info(f"💰 Proposing payment plan for phone: {request.phone}")
    
    try:
        # Get customer's current debt
        result = supabase.table('customers').select("*").eq('phone', request.phone).execute()
        
        if not result.data or len(result.data) == 0:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        customer = result.data[0]
        total_debt = float(customer['debt_amount'])
        
        # Mode 1: Installment Plan
        if request.installments:
            if request.installments < 1 or request.installments > 12:
                return ProposePaymentPlanResponse(
                    plan_type="installments",
                    total_amount=total_debt,
                    discount_applied=0.0,
                    accepted=False,
                    message="Number of installments must be between 1 and 12"
                )
            
            installment_amount = round(total_debt / request.installments, 2)
            payment_dates = generate_payment_dates(request.installments)
            
            logger.info(f"✅ Installment plan: {request.installments} payments of ${installment_amount}")
            
            return ProposePaymentPlanResponse(
                plan_type="installments",
                installment_amount=installment_amount,
                payment_dates=payment_dates,
                total_amount=total_debt,
                discount_applied=0.0,
                accepted=True,
                message=f"Payment plan of {request.installments} installments approved"
            )
        
        # Mode 2: Settlement Offer
        elif request.offer_amount:
            minimum_acceptable = total_debt * 0.80  # Must pay at least 80%
            
            if request.offer_amount >= minimum_acceptable:
                discount = total_debt - request.offer_amount
                logger.info(f"✅ Settlement accepted: ${request.offer_amount} (discount: ${discount})")
                
                return ProposePaymentPlanResponse(
                    plan_type="settlement",
                    total_amount=request.offer_amount,
                    discount_applied=round(discount, 2),
                    accepted=True,
                    message=f"Settlement offer of ${request.offer_amount} accepted"
                )
            else:
                logger.info(f"❌ Settlement rejected: ${request.offer_amount} < ${minimum_acceptable}")
                
                return ProposePaymentPlanResponse(
                    plan_type="settlement",
                    total_amount=total_debt,
                    discount_applied=0.0,
                    accepted=False,
                    message=f"Minimum acceptable amount is ${round(minimum_acceptable, 2)} (80% of debt)"
                )
        
        else:
            raise HTTPException(
                status_code=400,
                detail="Either 'installments' or 'offer_amount' must be provided"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error proposing payment plan: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/tools/update-status", response_model=UpdateStatusResponse)
async def update_status(request: UpdateStatusRequest):
    """
    Update customer status after call completion.
    
    Common statuses:
    - promised_to_pay: Customer agreed to pay
    - wrong_number: Wrong person answered
    - refused: Customer refused to pay
    - callback_requested: Customer asked to be called back
    - voicemail: Reached voicemail
    """
    logger.info(f"📝 Updating status for {request.phone} to '{request.new_status}'")
    
    try:
        # Update customer status
        update_data = {
            "status": request.new_status,
            "updated_at": datetime.now().isoformat()
        }
        
        result = supabase.table('customers').update(update_data).eq('phone', request.phone).execute()
        
        if not result.data or len(result.data) == 0:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        logger.info(f"✅ Status updated successfully")
        
        # Log the interaction summary if provided
        if request.summary:
            logger.info(f"📋 Call summary: {request.summary}")
        
        return UpdateStatusResponse(
            success=True,
            message=f"Status updated to '{request.new_status}'"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error updating status: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# ============================================================================
# STARTUP
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Log startup information."""
    logger.info("=" * 60)
    logger.info("🚀 Jess Voice Agent API Starting...")
    logger.info("=" * 60)
    logger.info("📡 Endpoints available:")
    logger.info("   GET  /health")
    logger.info("   POST /tools/get-case-details")
    logger.info("   POST /tools/propose-payment-plan")
    logger.info("   POST /tools/update-status")
    logger.info("=" * 60)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
