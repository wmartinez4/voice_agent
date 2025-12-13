"""
Jess Voice Agent - FastAPI Backend
Provides tool endpoints for ElevenLabs conversational AI agent.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, timedelta
from database import get_supabase_client
import logging
from logging.handlers import RotatingFileHandler
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging (similar to Serilog in .NET)
# Creates logs in both console and file
def setup_logging():
    """
    Configure logging with multiple outputs (console + file).
    Similar to Serilog configuration in .NET.
    """
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    # Define log format
    log_format = logging.Formatter(
        fmt='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)  # Set root to INFO to avoid noise from libraries
    
    # Remove existing handlers to avoid duplicates
    root_logger.handlers = []
    
    # Configure app logger separately for DEBUG
    app_logger = logging.getLogger("main")
    app_logger.setLevel(logging.DEBUG)
    
    # Handler 1: Console output (INFO level)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(log_format)
    root_logger.addHandler(console_handler)
    
    # Handler 2: File output - General logs (DEBUG level)
    file_handler = RotatingFileHandler(
        filename=f"logs/app_{datetime.now().strftime('%Y%m%d')}.log",
        maxBytes=10 * 1024 * 1024,  # 10MB per file
        backupCount=5,  # Keep 5 backup files
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(log_format)
    root_logger.addHandler(file_handler)
    
    # Handler 3: File output - Errors only (ERROR level)
    error_handler = RotatingFileHandler(
        filename=f"logs/errors_{datetime.now().strftime('%Y%m%d')}.log",
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(log_format)
    root_logger.addHandler(error_handler)
    
    return root_logger

# Initialize logging
setup_logging()
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

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize Supabase client
supabase = get_supabase_client()


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class GetCustomerNameRequest(BaseModel):
    phone: str = Field(..., description="Customer phone number")


class GetCustomerNameResponse(BaseModel):
    customer_name: str = Field(..., description="Customer full name for identity confirmation")


class GetCaseDetailsRequest(BaseModel):
    phone: str = Field(..., description="Customer phone number")


class GetCaseDetailsResponse(BaseModel):
    customer_name: str = Field(..., description="Customer full name")
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
# DASHBOARD/PANEL MODELS
# ============================================================================

class CustomerListItem(BaseModel):
    """Customer item for dashboard list"""
    id: str  # UUID in Supabase
    name: str
    phone: str
    debt_amount: float
    status: str
    risk_level: str
    due_date: str
    days_overdue: int
    last_call_date: Optional[str] = None
    updated_at: Optional[str] = None


class InitiateCallRequest(BaseModel):
    """Request to initiate a call to a customer"""
    phone: str = Field(..., description="Customer phone number to call")
    agent_id: Optional[str] = Field(None, description="Specific ElevenLabs Agent ID to use")


class InitiateCallResponse(BaseModel):
    """Response from call initiation"""
    success: bool
    conversation_id: Optional[str] = None
    message: str
    customer_name: Optional[str] = None


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

@app.get("/")
async def root():
    """Serve the landing page."""
    return FileResponse("static/landing.html")


@app.get("/dashboard")
async def dashboard():
    """Serve the dashboard HTML page."""
    return FileResponse("static/dashboard.html")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Jess Voice Agent API",
        "timestamp": datetime.now().isoformat()
    }


@app.post("/tools/get-customer-name", response_model=GetCustomerNameResponse)
async def get_customer_name(request: GetCustomerNameRequest):
    """
    Retrieve ONLY the customer name for identity verification.
    
    PRIVACY-FIRST: This endpoint should be called BEFORE revealing any 
    sensitive information. Use this to confirm you're speaking with the 
    right person, then call get-case-details after confirmation.
    """
    logger.info(f"🔍 Getting customer name for phone: {request.phone}")
    logger.debug(f"Request payload: {request.dict()}")
    
    try:
        # Query customer from database
        result = supabase.table('customers').select("name").eq('phone', request.phone).execute()
        
        if not result.data or len(result.data) == 0:
            logger.warning(f"⚠️  Customer not found: {request.phone}")
            raise HTTPException(status_code=404, detail="Customer not found")
        
        customer = result.data[0]
        
        response = GetCustomerNameResponse(
            customer_name=customer['name']
        )
        
        logger.info(f"✅ Customer name retrieved: {response.customer_name}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error retrieving customer name: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


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
            customer_name=customer['name'],
            debt_amount=float(customer['debt_amount']),
            due_date=customer['due_date'],
            risk_level=customer['risk_level'],
            days_overdue=days_overdue
        )
        
        logger.info(f"✅ Case details retrieved for {customer['name']}: ${response.debt_amount}, {days_overdue} days overdue")
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
# DASHBOARD/PANEL API ENDPOINTS
# ============================================================================

@app.get("/api/customers", response_model=List[CustomerListItem])
async def list_customers():
    """
    Get list of all customers for dashboard display.
    Returns customer information including debt status and last contact.
    """
    logger.info("📋 Fetching all customers for dashboard")
    
    try:
        # Query all customers from database
        result = supabase.table('customers').select("*").order('due_date', desc=False).execute()
        
        if not result.data:
            logger.info("No customers found")
            return []
        
        # Format customer data
        customers = []
        for customer in result.data:
            days_overdue = calculate_days_overdue(customer['due_date'])
            
            customers.append(CustomerListItem(
                id=customer['id'],
                name=customer['name'],
                phone=customer['phone'],
                debt_amount=float(customer['debt_amount']),
                status=customer.get('status', 'active'),
                risk_level=customer['risk_level'],
                due_date=customer['due_date'],
                days_overdue=days_overdue,
                last_call_date=customer.get('last_call_date'),
                updated_at=customer.get('updated_at')
            ))
        
        logger.info(f"✅ Retrieved {len(customers)} customers")
        return customers
        
    except Exception as e:
        logger.error(f"❌ Error fetching customers: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/api/agents")
async def list_agents():
    """
    Fetch available agents from ElevenLabs API.
    """
    logger.info("🤖 Fetching agents from ElevenLabs")
    
    ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
    if not ELEVENLABS_API_KEY:
        raise HTTPException(status_code=500, detail="ElevenLabs API Key not configured")
        
    url = "https://api.elevenlabs.io/v1/convai/agents"
    headers = {"xi-api-key": ELEVENLABS_API_KEY}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get('agents', [])
        else:
            logger.error(f"ElevenLabs Error: {response.text}")
            raise HTTPException(status_code=response.status_code, detail="Failed to fetch agents")
    except Exception as e:
        logger.error(f"Error fetching agents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/call", response_model=InitiateCallResponse)
async def initiate_call(request: InitiateCallRequest):
    """
    Initiate an outbound call to a customer via ElevenLabs API.
    Uses specific agent_id if provided, otherwise defaults to env var.
    """
    logger.info(f"📞 Initiating call to: {request.phone}")
    
    try:
        # Get customer info from database
        result = supabase.table('customers').select("*").eq('phone', request.phone).execute()
        
        if not result.data or len(result.data) == 0:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        customer = result.data[0]
        customer_name = customer['name']
        
        # ElevenLabs API configuration
        ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
        ELEVENLABS_AGENT_ID = os.getenv("ELEVENLABS_AGENT_ID")
        AGENT_PHONE_NUMBER_ID = os.getenv("AGENT_PHONE_NUMBER_ID")
        
        if not ELEVENLABS_API_KEY:
            logger.error("ElevenLabs credentials not configured")
            raise HTTPException(status_code=500, detail="ElevenLabs credentials not configured")
        
        # Use requested agent_id or fallback to env var
        agent_id_to_use = request.agent_id if request.agent_id else ELEVENLABS_AGENT_ID
        
        if not agent_id_to_use:
             raise HTTPException(status_code=500, detail="No Agent ID provided and default not set")

        # Prepare API request to ElevenLabs
        url = "https://api.elevenlabs.io/v1/convai/twilio/outbound-call"
        
        headers = {
            "xi-api-key": ELEVENLABS_API_KEY,
            "Content-Type": "application/json"
        }
        
        payload = {
            "agent_id": agent_id_to_use,
            "to_number": request.phone,
        }
        
        if AGENT_PHONE_NUMBER_ID:
            payload["agent_phone_number_id"] = AGENT_PHONE_NUMBER_ID
        
        # Add dynamic variables for the conversation
        payload["conversation_config_override"] = {
            "agent": {
                "dynamic_variables": {
                    "phone_number": request.phone,
                    "customer_name": customer_name
                }
            }
        }
        
        logger.info(f"Calling ElevenLabs API for {customer_name}")
        
        # Make API call to ElevenLabs
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            conversation_id = data.get('conversation_id', 'N/A')
            
            # Try to update last_call_date in database (if column exists)
            try:
                supabase.table('customers').update({
                    "updated_at": datetime.now().isoformat()
                }).eq('phone', request.phone).execute()
            except Exception as db_error:
                logger.warning(f"Could not update database timestamp: {db_error}")
            
            logger.info(f"✅ Call initiated successfully to {customer_name}")
            logger.info(f"   Conversation ID: {conversation_id}")
            
            return InitiateCallResponse(
                success=True,
                conversation_id=conversation_id,
                message=f"Call initiated successfully to {customer_name}",
                customer_name=customer_name
            )
        else:
            logger.error(f"ElevenLabs API error: {response.status_code} - {response.text}")
            return InitiateCallResponse(
                success=False,
                message=f"Failed to initiate call: {response.text}"
            )
            
    except HTTPException:
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ API request failed: {e}")
        raise HTTPException(status_code=503, detail="ElevenLabs API unavailable")
    except Exception as e:
        logger.error(f"❌ Error initiating call: {e}")
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
    logger.info("📡 Tool Endpoints:")
    logger.info("   GET  /health")
    logger.info("   POST /tools/get-customer-name")
    logger.info("   POST /tools/get-case-details")
    logger.info("   POST /tools/propose-payment-plan")
    logger.info("   POST /tools/update-status")
    logger.info("")
    logger.info("📊 Dashboard API Endpoints:")
    logger.info("   GET  /api/customers")
    logger.info("   POST /api/call")
    logger.info("=" * 60)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
