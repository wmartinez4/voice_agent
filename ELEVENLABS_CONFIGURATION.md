# ElevenLabs Agent Configuration Guide

This guide details exactly how to configure the "Jess" agent in ElevenLabs for the GenuVoice platform.

## 1. Agent Profile

- **Name:** Jess
- **Description:** Gentle Debt Recovery Agent
- **First Message:** `Hi! <break time="0.3s"/> This is Jess calling about your account.`
- **System Prompt:** Copy content from `jess_prompt_v2.txt` (English) or `jess_prompt_v2_es.txt` (Spanish).

## 2. Voice Settings

- **Recommended Voice:** Rachel (American, Calm) or Sarah (American, Soft).
- **Stability:** `0.50` (Natural variation)
- **Similarity:** `0.75` (Consistent identity)
- **Style Exaggeration:** `0.00` (Professional, not dramatic)
- **Speaker Boost:** `Enabled`

**Important:** Enable "SSML" in the agent settings to support pause tags (`<break time="..."/>`).

## 3. Tools Configuration

Configure these 4 tools in the "Tools" section.
**Base URL:** `https://genuvoice.com`

### Tool 1: get_customer_name
*Privacy-First: Gets name to verify identity before revealing debt.*

- **Name:** `get_customer_name`
- **Description:** `Get customer name for identity verification`
- **URL:** `https://genuvoice.com/tools/get-customer-name`
- **Method:** `POST`
- **Schema:**
```json
{
  "type": "object",
  "properties": {
    "phone": { "type": "string", "description": "Customer phone number (E.164)" }
  },
  "required": ["phone"]
}
```

### Tool 2: get_case_details
*Called ONLY after user says "Yes" to identity check.*

- **Name:** `get_case_details`
- **Description:** `Get debt details AFTER identity confirmed`
- **URL:** `https://genuvoice.com/tools/get-case-details`
- **Method:** `POST`
- **Schema:**
```json
{
  "type": "object",
  "properties": {
    "phone": { "type": "string", "description": "Customer phone number" }
  },
  "required": ["phone"]
}
```

### Tool 3: propose_payment_plan
*Calculates installments or valid settlements.*

- **Name:** `propose_payment_plan`
- **Description:** `Calculate payment plans or validate offers`
- **URL:** `https://genuvoice.com/tools/propose-payment-plan`
- **Method:** `POST`
- **Schema:**
```json
{
  "type": "object",
  "properties": {
    "phone": { "type": "string" },
    "installments": { "type": "integer", "description": "2, 3, or 4" },
    "offer_amount": { "type": "number", "description": "Settlement offer in USD" }
  },
  "required": ["phone"]
}
```

### Tool 4: update_status
*Updates database at end of call.*

- **Name:** `update_status`
- **Description:** `Update customer status after call`
- **URL:** `https://genuvoice.com/tools/update-status`
- **Method:** `POST`
- **Schema:**
```json
{
  "type": "object",
  "properties": {
    "phone": { "type": "string" },
    "new_status": { "type": "string", "enum": ["promised_to_pay", "refused", "callback_requested", "wrong_number", "voicemail"] },
    "summary": { "type": "string" }
  },
  "required": ["phone", "new_status"]
}
```

## 4. Privacy Flow Logic

The agent is strictly instructed to follow this flow:
1.  **Greeting** (Generic)
2.  **Tool Call:** `get_customer_name` -> Returns "Willian Martinez"
3.  **Verify:** "Am I speaking with Willian Martinez?"
4.  **Wait for "Yes"**
5.  **Tool Call:** `get_case_details` -> Returns Debt Info
6.  **Discuss Debt**

*(See `jess_prompt_v2.txt` for the specific instructions implementing this flow)*
