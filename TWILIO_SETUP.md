# Twilio + ElevenLabs Integration Guide

Complete step-by-step guide to set up phone numbers in Twilio and connect them with ElevenLabs for the Jess voice agent.

---

## Prerequisites

Before starting, you'll need:
- [ ] Twilio account (free trial available at https://www.twilio.com/try-twilio)
- [ ] ElevenLabs account with Conversational AI access
- [ ] Credit card for Twilio verification (required even for trial)
- [ ] Your backend API running and exposed via ngrok

---

## Part 1: Twilio Setup

### Step 1: Create Twilio Account

1. Go to https://www.twilio.com/try-twilio
2. Click "Sign up" or "Start for free"
3. Fill in your information:
   - Email
   - Password
   - First/Last name
4. Verify your email address
5. Complete phone verification (they'll send you a code)

**Trial Credits**: Twilio gives you $15-20 in trial credits to start

---

### Step 2: Get Your Twilio Credentials

After signing up, you'll need these credentials for ElevenLabs:

1. Go to Twilio Console: https://console.twilio.com/
2. On the dashboard, find and copy:
   - **Account SID** (starts with "AC...")
   - **Auth Token** (click "Show" to reveal it)

**IMPORTANT**: Keep these credentials secure - you'll need them for ElevenLabs integration.

```
Example format:
Account SID: ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
Auth Token: your_auth_token_here
```

---

### Step 3: Buy a Phone Number

#### Option A: Buy a Number (Recommended for Production)

1. In Twilio Console, go to **Phone Numbers** → **Manage** → **Buy a number**
   - Direct link: https://console.twilio.com/us1/develop/phone-numbers/manage/search

2. Select your preferences:
   - **Country**: Choose your country (e.g., United States)
   - **Capabilities**: Check "Voice" (required for calls)
   - **Number type**: Local or Toll-Free
     - **Local**: Cheaper (~$1/month), looks like regular number
     - **Toll-Free**: More expensive (~$2/month), looks more professional

3. Click "Search" to see available numbers

4. Choose a number you like and click "Buy"

5. Confirm the purchase

**Costs**:
- Local number: ~$1.00/month
- Toll-Free: ~$2.00/month
- Outbound calls: ~$0.01-0.02/minute
- Inbound calls: ~$0.0085/minute

#### Option B: Use Trial Number (For Testing Only)

If you're on trial:
1. Twilio provides a trial number automatically
2. **Limitation**: Can only call verified numbers
3. To verify a number:
   - Go to **Phone Numbers** → **Manage** → **Verified Caller IDs**
   - Add your personal number for testing

---

### Step 4: Configure the Phone Number (SKIP THIS - ElevenLabs will do it)

**IMPORTANT**: You do NOT need to configure webhooks manually in Twilio. ElevenLabs will automatically configure your Twilio number when you connect it.

Just make sure you have:
- ✅ A phone number purchased
- ✅ Your Account SID
- ✅ Your Auth Token

---

## Part 2: ElevenLabs Setup

### Step 1: Access Conversational AI

1. Log in to ElevenLabs: https://elevenlabs.io
2. Navigate to **Conversational AI** section
3. Create a new agent or select "Jess" if already created

---

### Step 2: Connect Twilio to ElevenLabs

1. In your ElevenLabs agent settings, find **Telephony** or **Phone Integration** section

2. Click **"Connect Twilio"** or **"Add Phone Number"**

3. Enter your Twilio credentials:
   ```
   Account SID: ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   Auth Token: your_auth_token_here
   ```

4. Click **"Connect"** or **"Authorize"**

5. ElevenLabs will:
   - Verify your Twilio credentials
   - Fetch your available phone numbers
   - Show you a list of numbers to choose from

6. Select the phone number you want to use for Jess

7. ElevenLabs will automatically:
   - Configure the webhook URLs in Twilio
   - Set up call routing
   - Enable voice capabilities

**That's it!** ElevenLabs handles all the technical configuration.

---

### Step 3: Configure Agent Tools (Backend Integration)

Now you need to connect your FastAPI backend to the agent:

1. Make sure your backend is running:
   ```bash
   uvicorn main:app --reload
   ```

2. Expose it with ngrok:
   ```bash
   ngrok http 8000
   ```
   Copy the HTTPS URL (e.g., `https://abc123.ngrok.io`)

3. In ElevenLabs agent settings, go to **Tools** or **Client Tools**

4. Add each tool (See `ELEVENLABS_CONFIGURATION.md` for full details):

- **Tool 1**: `get_customer_name`
- **Tool 2**: `get_case_details`
- **Tool 3**: `propose_payment_plan`
- **Tool 4**: `update_status`

---

### Step 4: Configure System Prompt

1. In ElevenLabs agent settings, find **System Prompt** or **Instructions**

2. Open the file: `/Users/willianmartinez/voice_agent/jess_prompt_v2.txt`

3. Select all (Cmd+A) and copy (Cmd+C)

4. Paste into the ElevenLabs system prompt field

5. Save the configuration

---

### Step 5: Configure Voice Settings

1. In agent settings, go to **Voice** section

2. Select a voice:
   - **Recommended**: Rachel, Sarah, or any professional female voice
   - Preview different voices to find the best fit

3. Adjust voice settings:
   - **Stability**: 0.6-0.7 (natural but consistent)
   - **Similarity**: 0.7-0.8 (clear and recognizable)
   - **Style**: 0.3-0.4 (conversational but professional)

4. **IMPORTANT**: Enable **SSML** (Speech Synthesis Markup Language)
   - This allows the `<break time="0.3s"/>` pause tags to work
   - Look for "SSML Support" or "Advanced Settings"
   - Toggle it ON

---

### Step 6: Configure Conversation Settings

1. **Language**: English (or your preferred language)

2. **Interruptions**: Enable (allows customer to interrupt Jess)

3. **Maximum silence**: 3-4 seconds before asking if customer is still there

4. **Speed**: Normal (not too fast)

5. **Model Selection**: 
   - **Recommended**: GPT-4o or GLM 4.5 Air (balanced latency/accuracy)
   - For ultra-low latency: Gemini 2.5 Flash Lite
   - For complex reasoning: Claude Sonnet 4

---

## Part 3: Testing the Integration

### Test 1: Verify Backend Connection

1. Test your API is accessible:
   ```bash
   curl https://your-ngrok-url.ngrok.io/health
   ```
   Should return: `{"status": "healthy", ...}`

2. Test a tool endpoint:
   ```bash
   curl -X POST https://your-ngrok-url.ngrok.io/tools/get-case-details \
     -H "Content-Type: application/json" \
     -d '{"phone": "+15551234567"}'
   ```

---

### Test 2: Make a Test Call

#### Option A: Outbound Call (Jess calls you)

1. In ElevenLabs, use the **"Test Call"** feature

2. Enter a test phone number:
   - Use one of your seeded numbers: `+15551234567`
   - Or your personal number (if verified in Twilio trial)

3. Click **"Start Call"**

4. Answer the phone and interact with Jess

5. Verify:
   - ✅ Jess greets you naturally
   - ✅ She calls `get_case_details` after identity confirmation
   - ✅ She presents debt information
   - ✅ She offers payment options
   - ✅ She calls `update_status` at the end

#### Option B: Inbound Call (You call Jess)

1. From your phone, dial the Twilio number you configured

2. Jess should answer automatically

3. Interact with the agent

**Note**: Inbound calls may require additional configuration in ElevenLabs

---

### Test 3: Check Database Updates

After a test call:

1. Check your Supabase database:
   ```bash
   # Or use Supabase dashboard
   ```

2. Verify the customer status was updated

3. Check the `updated_at` timestamp changed

---

## Part 4: Monitoring and Debugging

### View Call Logs in Twilio

1. Go to Twilio Console → **Monitor** → **Logs** → **Calls**
   - https://console.twilio.com/us1/monitor/logs/calls

2. You'll see:
   - Call duration
   - Cost
   - Status (completed, failed, etc.)
   - Recording (if enabled)

---

### View Conversation Logs in ElevenLabs

1. In ElevenLabs, go to **Analytics** or **Conversations**

2. You'll see:
   - Transcript of conversation
   - Tool calls made
   - Success/failure metrics
   - Audio recording

---

### Common Issues and Solutions

#### Issue 1: "Tool not found" or "Tool failed"

**Solution**:
- Verify ngrok is still running
- Check the ngrok URL hasn't changed (ngrok free tier changes URLs on restart)
- Test the endpoint manually with curl
- Check FastAPI logs for errors

#### Issue 2: "Unable to connect to Twilio"

**Solution**:
- Verify Account SID and Auth Token are correct
- Check Twilio account is active (not suspended)
- Ensure you have credits in Twilio

#### Issue 3: "SSML tags being spoken literally"

**Solution**:
- Enable SSML in ElevenLabs voice settings
- Check that you're using correct SSML syntax: `<break time="0.3s"/>`

#### Issue 4: "Customer not found in database"

**Solution**:
- Run seed data script: `python seed_data.py`
- Verify phone number format (should be E.164: `+15551234567`)
- Check Supabase connection in `.env` file

#### Issue 5: "Call connects but Jess doesn't respond"

**Solution**:
- Check system prompt is configured correctly
- Verify voice is selected
- Check ElevenLabs conversation logs for errors
- Ensure model is selected (GPT-4o, etc.)

---

## Part 5: Production Deployment

### When Ready for Production:

1. **Upgrade Twilio Account**:
   - Remove trial limitations
   - Add payment method
   - Buy production phone number

2. **Replace Ngrok**:
   - Deploy FastAPI to production (Railway, Render, AWS, etc.)
   - Use a real domain with HTTPS
   - Update tool URLs in ElevenLabs

3. **Add Authentication**:
   - Implement API key authentication on your endpoints
   - Configure in ElevenLabs tool settings

4. **Enable Monitoring**:
   - Set up logging and alerts
   - Monitor call success rates
   - Track tool call failures

5. **Compliance**:
   - Review call recording policies
   - Ensure TCPA compliance (US)
   - Add opt-out mechanisms

---

## Costs Breakdown

### Twilio Costs:
- **Phone number**: $1-2/month
- **Outbound calls**: ~$0.01-0.02/minute
- **Inbound calls**: ~$0.0085/minute
- **SMS** (if needed): ~$0.0075/message

### ElevenLabs Costs:
- Check your plan pricing at https://elevenlabs.io/pricing
- Conversational AI typically charged per minute of conversation

### Example Monthly Cost (100 calls, 3 min avg):
- Twilio number: $1
- Twilio calls: 100 × 3 min × $0.015 = $4.50
- ElevenLabs: Depends on your plan
- **Total Twilio**: ~$5.50/month

---

## Quick Reference: What You Need

### From Twilio:
- ✅ Account SID
- ✅ Auth Token
- ✅ Phone number (purchased)

### From Your Backend:
- ✅ Ngrok URL (or production URL)
- ✅ API running on port 8000
- ✅ Supabase configured

### In ElevenLabs:
- ✅ Agent created
- ✅ Twilio connected
- ✅ System prompt configured
- ✅ 3 tools configured
- ✅ Voice selected
- ✅ SSML enabled

---

## Next Steps

1. **Test thoroughly** with different scenarios
2. **Monitor first calls** closely
3. **Iterate on prompt** based on real conversations
4. **Add more test data** to Supabase
5. **Plan production deployment**

---

## Support Resources

- **Twilio Docs**: https://www.twilio.com/docs/voice
- **ElevenLabs Docs**: https://elevenlabs.io/docs
- **Twilio Support**: https://support.twilio.com
- **ElevenLabs Support**: support@elevenlabs.io

---

**You're all set!** 🚀

Follow these steps in order, and you'll have Jess making calls in no time.
