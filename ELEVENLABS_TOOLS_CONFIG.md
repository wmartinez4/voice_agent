# ElevenLabs Tools Configuration

Use these settings to configure your agent tools in ElevenLabs.
**Current Ngrok URL:** `https://6bbe6706adc5.ngrok-free.app`

## Tool 1: get_case_details

- **Name:** `get_case_details`
- **Description:** `Retrieves customer debt information after identity confirmation`
- **URL:** `https://6bbe6706adc5.ngrok-free.app/tools/get-case-details`
- **Method:** `POST`
- **Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "phone": {
      "type": "string",
      "description": "Customer phone number in E.164 format (e.g. +15551234567)"
    }
  },
  "required": [
    "phone"
  ]
}
```

## Tool 2: propose_payment_plan

- **Name:** `propose_payment_plan`
- **Description:** `Calculates payment plans or validates settlement offers`
- **URL:** `https://6bbe6706adc5.ngrok-free.app/tools/propose-payment-plan`
- **Method:** `POST`
- **Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "phone": {
      "type": "string",
      "description": "Customer phone number"
    },
    "installments": {
      "type": "integer",
      "description": "Number of installments (2, 3, or 4)"
    },
    "offer_amount": {
      "type": "number",
      "description": "Settlement offer amount in dollars"
    }
  },
  "required": [
    "phone"
  ]
}
```

## Tool 3: update_status

- **Name:** `update_status`
- **Description:** `Updates customer status after call completion`
- **URL:** `https://6bbe6706adc5.ngrok-free.app/tools/update-status`
- **Method:** `POST`
- **Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "phone": {
      "type": "string",
      "description": "Customer phone number"
    },
    "new_status": {
      "type": "string",
      "description": "Outcome status: promised_to_pay, wrong_number, refused, callback_requested, voicemail, hung_up, escalated, already_paid"
    },
    "summary": {
      "type": "string",
      "description": "Brief summary of the interaction and agreement details"
    }
  },
  "required": [
    "phone",
    "new_status"
  ]
}
```
