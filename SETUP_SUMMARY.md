# Setup Summary - Privacy-First Flow

Complete configuration for Jess Voice Agent with the new privacy-first approach.

---

## ✅ What's Been Done

### Backend Updates:
- ✅ New endpoint: `/tools/get-customer-name` - Returns only customer name
- ✅ Updated endpoint: `/tools/get-case-details` - Now includes customer_name in response
- ✅ Server running on: `http://localhost:8000`
- ✅ Exposed via ngrok: `https://daec0fa726f0.ngrok-free.app`

### Database:
- ✅ Single customer: Willian Martinez (+573124199685)
- ✅ Debt: $664.0
- ✅ Status: active

### Documentation:
- ✅ `jess_prompt.txt` - Updated with new privacy-first flow
- ✅ `prompt_guide.md` - Updated with new tool and examples
- ✅ `ELEVENLABS_TOOLS_CONFIG.md` - Updated with 4 tools configuration

---

## 🔧 What You Need to Configure in ElevenLabs

### Step 1: Update Tools (4 Tools Total)

Go to your agent in ElevenLabs Dashboard → Tools section

#### **Tool 1: get_customer_name** (NEW - ADD THIS)

```
Name: get_customer_name
Description: Get customer name for identity verification before revealing debt info
URL: https://daec0fa726f0.ngrok-free.app/tools/get-customer-name
Method: POST

Parameters (JSON Schema):
{
  "type": "object",
  "properties": {
    "phone": {
      "type": "string",
      "description": "Customer phone number in E.164 format"
    }
  },
  "required": ["phone"]
}
```

#### **Tool 2: get_case_details** (UPDATE URL)

```
Name: get_case_details
Description: Get debt details AFTER identity confirmed
URL: https://daec0fa726f0.ngrok-free.app/tools/get-case-details
Method: POST

Parameters (JSON Schema):
{
  "type": "object",
  "properties": {
    "phone": {
      "type": "string",
      "description": "Customer phone number"
    }
  },
  "required": ["phone"]
}
```

#### **Tool 3: propose_payment_plan** (UPDATE URL)

```
Name: propose_payment_plan
Description: Calculate payment plans or validate settlement offers
URL: https://daec0fa726f0.ngrok-free.app/tools/propose-payment-plan
Method: POST

Parameters (JSON Schema):
{
  "type": "object",
  "properties": {
    "phone": {
      "type": "string",
      "description": "Customer phone number"
    },
    "installments": {
      "type": "integer",
      "description": "Number of installments (2-4)"
    },
    "offer_amount": {
      "type": "number",
      "description": "Settlement offer amount"
    }
  },
  "required": ["phone"]
}
```

#### **Tool 4: update_status** (UPDATE URL)

```
Name: update_status
Description: Update customer status after call completion
URL: https://daec0fa726f0.ngrok-free.app/tools/update-status
Method: POST

Parameters (JSON Schema):
{
  "type": "object",
  "properties": {
    "phone": {
      "type": "string",
      "description": "Customer phone number"
    },
    "new_status": {
      "type": "string",
      "description": "Call outcome status"
    },
    "summary": {
      "type": "string",
      "description": "Brief interaction summary"
    }
  },
  "required": ["phone", "new_status"]
}
```

---

### Step 2: Update System Prompt

Go to your agent → System Prompt / Instructions

**Copy the ENTIRE content from:** `/Users/willianmartinez/voice_agent/jess_prompt.txt`

**Or use this summary:**

#### Key Changes:

1. **Add at the beginning:**
```
CRITICAL: PRIVACY-FIRST FLOW

You must ALWAYS follow this sequence:
1. Greet customer generically
2. Call get_customer_name(phone) FIRST
3. Ask: "Am I speaking with {customer_name}?"
4. Wait for confirmation
5. ONLY AFTER confirmation, call get_case_details(phone)
6. Use customer name throughout conversation

NEVER reveal debt information before steps 1-4 are complete.
```

2. **Tool Call Order:**
   - First: `get_customer_name` → Get name
   - Second: `get_case_details` → Get debt info (after confirmation)
   - Third: `propose_payment_plan` → If needed
   - Fourth: `update_status` → At end

---

### Step 3: Update First Message (Optional)

In ElevenLabs Dashboard → First Message:

**Change from:**
```
Hi! <break time="0.3s"/> I was hoping to catch willian Martinez?
```

**To (Generic):**
```
Hi! <break time="0.3s"/> This is Jess calling about your account.
```

This is now generic because Jess will get the name dynamically via `get_customer_name`.

---

## 🎯 Expected Flow After Configuration

```
1. Call initiated from script: python make_call.py +573124199685

2. Phone rings

3. Customer answers

4. Jess: "Hi! This is Jess calling about your account."

5. Jess (internally): Calls get_customer_name("+573124199685")
   Response: {"customer_name": "Willian Martinez"}

6. Jess: "Am I speaking with Willian Martinez?"

7. Customer: "Yes, that's me"

8. Jess: "Thank you for confirming, Willian."

9. Jess (internally): Calls get_case_details("+573124199685")
   Response: {
     "customer_name": "Willian Martinez",
     "debt_amount": 664.0,
     "due_date": "2025-11-18",
     "risk_level": "low",
     "days_overdue": 7
   }

10. Jess: "Willian, I'm calling about something I noticed on your account."
    <break time="0.4s"/>
    "There's an outstanding balance of $664 from about 7 days ago."
    <break time="0.3s"/>
    "Were you aware of this pending amount?"

11. [Negotiation continues...]

12. Jess (internally): Calls update_status at end
```

---

## 🧪 How to Test

### Test 1: Verify Endpoints Work

```bash
# Test get_customer_name
curl -X POST http://localhost:8000/tools/get-customer-name \
  -H "Content-Type: application/json" \
  -d '{"phone": "+573124199685"}'

# Expected: {"customer_name":"Willian Martinez"}

# Test get_case_details
curl -X POST http://localhost:8000/tools/get-case-details \
  -H "Content-Type: application/json" \
  -d '{"phone": "+573124199685"}'

# Expected: {"customer_name":"Willian Martinez","debt_amount":664.0,...}
```

### Test 2: Make Real Call

```bash
python make_call.py +573124199685
```

Watch for:
- ✅ Jess says your name correctly
- ✅ Jess asks for confirmation BEFORE mentioning debt
- ✅ Jess uses your name throughout conversation

### Test 3: Monitor in Ngrok Dashboard

```bash
open http://127.0.0.1:4040
```

You should see TWO API calls during the conversation:
1. `POST /tools/get-customer-name` (first)
2. `POST /tools/get-case-details` (after confirmation)

---

## 📝 Checklist

Before making next test call, ensure:

- [ ] Tool 1 (get_customer_name) added in ElevenLabs
- [ ] Tool 2, 3, 4 URLs updated with new ngrok URL
- [ ] System prompt updated with privacy-first instructions
- [ ] First message is generic (not hardcoded name)
- [ ] Backend server running (uvicorn)
- [ ] Ngrok running and exposing port 8000

---

## 🎯 Next Steps

1. **Configure the 4 tools in ElevenLabs** (see Step 1 above)
2. **Update system prompt** with content from `jess_prompt.txt`
3. **Test with:** `python make_call.py +573124199685`
4. **Verify Jess:**
   - Calls `get_customer_name` first
   - Says "Willian Martinez" correctly
   - Asks for confirmation
   - THEN calls `get_case_details`
   - Uses your name throughout

---

## ⚠️ Important Notes

- **Ngrok URL changes** every time you restart ngrok
  - Current: `https://daec0fa726f0.ngrok-free.app`
  - If you restart ngrok, update all 4 tool URLs in ElevenLabs

- **Privacy-First** is critical
  - NEVER reveal debt before identity confirmation
  - Always call `get_customer_name` FIRST

- **Test thoroughly** before adding more customers

---

**Ready to test?** Configure the tools in ElevenLabs and make another call! 🚀

