# Outbound Calls Guide - ElevenLabs + Supabase

Complete guide to trigger outbound calls using ElevenLabs Conversational AI with customer data from Supabase.

---

## 🎯 **Complete Flow**

```
1. Python Script (make_call.py)
   ↓
2. Query Supabase → Get customer (phone + name)
   ↓
3. Call ElevenLabs API → Start outbound call
   ↓
4. ElevenLabs + Twilio → Make phone call
   ↓
5. During call, Jess agent:
   - Greets with customer name (dynamic)
   - Confirms identity
   - Calls get-case-details → Gets debt info
   - Negotiates payment
   - Calls update-status → Saves result
```

---

## 📋 **Prerequisites**

### ✅ Already Configured:
- [x] ElevenLabs agent created
- [x] Twilio connected to ElevenLabs
- [x] Backend API running (FastAPI)
- [x] Ngrok exposing API
- [x] Supabase database with customers

### ⚠️ Still Needed:
- [ ] Get `AGENT_PHONE_NUMBER_ID` from ElevenLabs
- [ ] Configure first message in ElevenLabs dashboard
- [ ] Test with a real call

---

## 🔑 **Get AGENT_PHONE_NUMBER_ID**

### Method 1: ElevenLabs Dashboard

1. Go to [ElevenLabs Dashboard](https://elevenlabs.io/app/conversational-ai)
2. Select your agent "Jess"
3. Go to **Telephony** or **Phone Numbers** section
4. You should see your connected Twilio phone number
5. Look for the **Phone Number ID** (starts with `pn_` or similar)

### Method 2: API Call

```bash
curl -X GET "https://api.elevenlabs.io/v1/convai/phone-numbers" \
  -H "xi-api-key: YOUR_API_KEY"
```

Response will show your phone numbers with their IDs.

### Add to .env

Once you have the ID, add it to your `.env` file:

```bash
AGENT_PHONE_NUMBER_ID=pn_your_phone_number_id_here
```

---

## 🎤 **Customize First Message with Customer Name**

### Current Setup (Hard-coded):
```
"Hi! <break time="0.3s"/> I was hoping to catch willian Martinez?"
```

### Dynamic Solution:

The script now passes the customer name dynamically:

```python
"conversation_initiation_client_data": {
    "first_message": f"Hi! <break time=\"0.3s\"/> I was hoping to catch {customer_name}? <break time=\"0.3s\"/> Is that you?"
}
```

**How it works:**
- Script queries Supabase: `SELECT name FROM customers WHERE phone = '+573124199685'`
- Gets: `"Willian Martinez"`
- Passes to ElevenLabs API with the phone number
- Jess says: "Hi! I was hoping to catch Willian Martinez? Is that you?"

---

## 🎯 **Customer Selection Criteria**

The script selects customers based on **priority**:

### Priority Order:
1. **Status = 'active'** (only active customers)
2. **Risk Level** (high > medium > low)
3. **Days Overdue** (oldest first)

### Example Query Result:

| Priority | Customer | Phone | Debt | Risk | Days |
|----------|----------|-------|------|------|------|
| **1st** | Carlos Rodríguez | +15559876543 | $1,200 | high | 45 |
| **2nd** | Willian Martinez | +573124199685 | $664 | low | 7 |
| ~~Skip~~ | María González | +15551234567 | $500 | medium | ~~promised_to_pay~~ |

### Code Implementation:

```python
def get_next_customer_to_call():
    supabase = get_supabase_client()
    
    # Get active customers, ordered by due date
    result = supabase.table('customers') \
        .select('*') \
        .eq('status', 'active') \
        .order('due_date', desc=False) \
        .execute()
    
    # Sort by risk level (high > medium > low)
    risk_priority = {'high': 1, 'medium': 2, 'low': 3}
    sorted_customers = sorted(
        result.data, 
        key=lambda x: (risk_priority.get(x['risk_level'], 999), x['due_date'])
    )
    
    return sorted_customers[0]  # Return highest priority
```

---

## 🚀 **How to Make Calls**

### Option 1: Auto-Select Next Customer (Recommended)

```bash
python make_call.py
```

**What happens:**
1. Queries Supabase for highest priority customer
2. Shows customer details
3. Asks for confirmation
4. Calls ElevenLabs API
5. Jess makes the call

**Output:**
```
📋 Auto-selecting next customer to call based on priority...

Selected: Carlos Rodríguez
  Phone: +15559876543
  Debt: $1200.0
  Risk: high
  Due date: 2025-10-11

Proceed with call? (yes/no): yes

============================================================
📞 ElevenLabs Outbound Call
============================================================
Customer: Carlos Rodríguez
Phone: +15559876543
Agent ID: agent_8701kaydfsgkf06ryjpg7hqd9am2

Initiating call...

Status Code: 200

✅ Call initiated successfully!

  Conversation ID: conv_abc123xyz
  Status: initiated
```

---

### Option 2: Call Specific Phone Number

```bash
python make_call.py +573124199685
```

**What happens:**
1. Looks up phone number in Supabase
2. Gets customer name
3. Makes call with personalized greeting

**If customer exists in DB:**
```
Customer: Willian Martinez
Phone: +573124199685
```

**If customer NOT in DB:**
```
⚠️  Customer not found in database, calling anyway...
Customer: the account holder
Phone: +573124199685
```

---

## 📞 **What Happens During the Call**

### 1. **First Message (Dynamic)**
```
Jess: "Hi! I was hoping to catch Willian Martinez? Is that you?"
```

### 2. **Identity Confirmation**
```
Customer: "Yes, that's me"
Jess: [Internally calls get-case-details("+573124199685")]
```

### 3. **Get Debt Information**
```json
{
  "debt_amount": 664.0,
  "due_date": "2025-11-18",
  "risk_level": "low",
  "days_overdue": 7
}
```

### 4. **Present Information**
```
Jess: "I'm calling about something quick I noticed on your account.
       There's an outstanding balance of $664 from about 7 days ago.
       Were you aware of this pending amount?"
```

### 5. **Negotiate Payment**
```
Customer: "Can I pay in installments?"
Jess: [Calls propose-payment-plan(phone="+573124199685", installments=3)]
Jess: "Perfect, that would be $221.33 each. What dates work best for you?"
```

### 6. **Close Call**
```
Jess: [Calls update-status(phone="+573124199685", status="promised_to_pay")]
Jess: "Thank you for your time, Willian. If you need anything, let me know."
```

---

## 🔧 **Alternative Selection Criteria**

### By Debt Amount (Highest First):
```python
result = supabase.table('customers') \
    .select('*') \
    .eq('status', 'active') \
    .order('debt_amount', desc=True) \
    .limit(1) \
    .execute()
```

### By Days Overdue Only:
```python
result = supabase.table('customers') \
    .select('*') \
    .eq('status', 'active') \
    .order('due_date', desc=False) \
    .limit(1) \
    .execute()
```

### Round Robin (Avoid Repeat Calls):

**First, add column to database:**
```sql
ALTER TABLE customers ADD COLUMN last_call_date TIMESTAMP;
```

**Then query:**
```python
result = supabase.table('customers') \
    .select('*') \
    .eq('status', 'active') \
    .order('last_call_date', desc=False) \
    .limit(1) \
    .execute()
```

**Update after call:**
```python
supabase.table('customers') \
    .update({'last_call_date': datetime.now().isoformat()}) \
    .eq('phone', customer_phone) \
    .execute()
```

---

## ⚠️ **Troubleshooting**

### Error: 404 Not Found
**Cause:** Missing `AGENT_PHONE_NUMBER_ID` or wrong endpoint

**Solution:**
1. Get your phone number ID from ElevenLabs dashboard
2. Add to `.env`: `AGENT_PHONE_NUMBER_ID=pn_...`

---

### Error: 401 Unauthorized
**Cause:** Invalid API key

**Solution:**
1. Check `ELEVENLABS_API_KEY` in `.env`
2. Verify it's correct in [ElevenLabs Dashboard](https://elevenlabs.io/app/settings)

---

### Error: 400 Bad Request - "to_number is required"
**Cause:** Phone number format incorrect

**Solution:**
- Use E.164 format: `+573124199685` (not `3124199685`)
- Include country code: `+` + country + number

---

### Call Connects but Jess Doesn't Call Backend
**Cause:** Tools not configured correctly in ElevenLabs

**Solution:**
1. Verify tool URLs in ElevenLabs dashboard point to `https://genuvoice.com` (or your ngrok if testing locally)
2. Test endpoints manually:
   ```bash
   curl -X POST https://genuvoice.com/tools/get-case-details \
     -H "Content-Type: application/json" \
     -d '{"phone": "+573124199685"}'
   ```

---

## 📊 **Monitor Calls**

### View in ElevenLabs Dashboard:
1. Go to [ElevenLabs Dashboard](https://elevenlabs.io/app/conversational-ai)
2. Select your agent
3. Go to **Analytics** or **Conversations**
4. See transcripts, tool calls, and audio recordings

### View in Ngrok (Local Testing Only):
```bash
# Open ngrok web interface
open http://127.0.0.1:4040
```
Shows all HTTP requests made by Jess to your backend if running locally.

### View Backend Logs (Production):
```bash
# SSH into AWS
ssh -i ~/.ssh/voice-agent-key.pem ec2-user@3.219.214.103

# Watch Docker logs
docker logs -f jess-voice-agent
```

### View Backend Logs:
Check terminal where FastAPI is running for real-time logs

---

## 🎯 **Best Practices**

### 1. Test with Your Own Phone First
```bash
python make_call.py +YOUR_PHONE_NUMBER
```

### 2. Start with Low-Risk Customers
Filter by risk_level = 'low' for initial testing

### 3. Monitor First Few Calls
Watch the full conversation in ElevenLabs dashboard

### 4. Update Status After Each Call
Jess should call `update-status` endpoint automatically

### 5. Avoid Over-Calling
Wait at least 48 hours between calls to same customer

---

## 📝 **Summary**

✅ **Script**: `make_call.py` - Triggers outbound calls  
✅ **Database**: Supabase - Stores customer data  
✅ **Selection**: Priority-based (risk + overdue days)  
✅ **Personalization**: Dynamic first message with customer name  
✅ **Flow**: Greet → Confirm → Get Details → Negotiate → Update  

**Next Step**: Get your `AGENT_PHONE_NUMBER_ID` and test the first call! 🚀

