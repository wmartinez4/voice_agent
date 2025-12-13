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

Import the following JSON files directly into the ElevenLabs "Tools" section.
These files are located in the `tools_config/` directory of this project.

**Base URL:** `https://genuvoice.com`

### Tool 1: get_customer_name
*Privacy-First: Gets name to verify identity before revealing debt.*

- **File:** `tools_config/tool_1_get_customer_name.json`
- **Description:** `Retrieves only the customer name for identity verification`
- **Dynamic Variable:** `phome` -> `system__called_number`

### Tool 2: get_case_details
*Called ONLY after user says "Yes" to identity check.*

- **File:** `tools_config/tool_2_get_case_details.json`
- **Description:** `Get debt details AFTER identity confirmed`

### Tool 3: propose_payment_plan
*Calculates installments or valid settlements.*

- **File:** `tools_config/tool_3_propose_payment_plan.json`
- **Description:** `Calculate payment plans or validate offers`

### Tool 4: update_status
*Updates database at end of call.*

- **File:** `tools_config/tool_4_update_status.json`
- **Description:** `Update customer status after call`

*(See the `tools_config/` folder for the full JSON schemas to copy/paste)*

## 4. Privacy Flow Logic

The agent is strictly instructed to follow this flow:
1.  **Greeting** (Generic)
2.  **Tool Call:** `get_customer_name` -> Returns "Willian Martinez"
3.  **Verify:** "Am I speaking with Willian Martinez?"
4.  **Wait for "Yes"**
5.  **Tool Call:** `get_case_details` -> Returns Debt Info
6.  **Discuss Debt**

*(See `jess_prompt_v2.txt` for the specific instructions implementing this flow)*
