# Next Steps: Getting Jess Ready to Call

Your ElevenLabs agent "Jess" is configured! Here's what you need to do next to start making calls.

---

## ✅ What's Already Done

- [x] ElevenLabs agent created and configured
- [x] Agent ID and API key saved in `.env` file
- [x] System prompt ready in `jess_prompt.txt`
- [x] Backend API code ready (`main.py`)
- [x] Database scripts ready

---

## 🔧 Step 1: Configure Supabase (Required)

You need to add your Supabase credentials to the `.env` file.

### Get Your Supabase Credentials:

1. Go to https://supabase.com and sign in (or create account)
2. Create a new project (or use existing one)
3. Go to **Project Settings** → **API**
4. Copy these values:
   - **Project URL** (looks like: `https://xxxxx.supabase.co`)
   - **anon/public key** (starts with `eyJ...`)

### Update Your `.env` File:

Open `/Users/willianmartinez/voice_agent/.env` and replace:

```bash
SUPABASE_URL=your_supabase_project_url_here
SUPABASE_KEY=your_supabase_anon_or_service_key_here
```

With your actual credentials:

```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## 🗄️ Step 2: Setup Database

### Run the setup script:

```bash
cd /Users/willianmartinez/voice_agent
python setup_db.py
```

This will show you SQL to run in Supabase.

### Execute SQL in Supabase:

1. Go to your Supabase project
2. Click **SQL Editor** in the left sidebar
3. Click **New Query**
4. Copy the SQL from the terminal output
5. Paste it and click **Run**

### Load Test Data:

```bash
python seed_data.py
```

This creates 3 test customers:
- María González: +15551234567 ($500, 15 days overdue)
- Carlos Rodríguez: +15559876543 ($1,200, 45 days overdue)
- Ana Martínez: +15555555555 ($250, 7 days overdue)

---

## 🚀 Step 3: Start Your Backend API

### Start the FastAPI server:

```bash
uvicorn main:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     🚀 Jess Voice Agent API Starting...
```

### Test it works:

Open another terminal and run:

```bash
curl http://localhost:8000/health
```

Should return:
```json
{
  "status": "healthy",
  "service": "Jess Voice Agent API",
  "timestamp": "2025-11-25T..."
}
```

---

## 🌐 Step 4: Expose API with Ngrok

Your backend needs to be accessible from the internet for ElevenLabs to call it.

### Install ngrok (if not installed):

```bash
brew install ngrok
# or download from https://ngrok.com/download
```

### Start ngrok:

In a NEW terminal (keep uvicorn running):

```bash
ngrok http 8000
```

### Copy the HTTPS URL:

You'll see something like:
```
Forwarding   https://abc123.ngrok.io -> http://localhost:8000
```

**Copy the HTTPS URL** (e.g., `https://abc123.ngrok.io`)

---

## 🔧 Step 5: Configure Tools in ElevenLabs

Go back to your ElevenLabs agent settings and add the 3 tools:

### Tool 1: get_case_details

- **Name**: `get_case_details`
- **Description**: "Retrieves customer debt information after identity confirmation"
- **URL**: `https://YOUR-NGROK-URL.ngrok.io/tools/get-case-details`
- **Method**: POST
- **Parameters**:
```json
{
  "phone": {
    "type": "string",
    "description": "Customer phone number"
  }
}
```

### Tool 2: propose_payment_plan

- **Name**: `propose_payment_plan`
- **Description**: "Calculates payment plans or validates settlement offers"
- **URL**: `https://YOUR-NGROK-URL.ngrok.io/tools/propose-payment-plan`
- **Method**: POST
- **Parameters**:
```json
{
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
}
```

### Tool 3: update_status

- **Name**: `update_status`
- **Description**: "Updates customer status after call completion"
- **URL**: `https://YOUR-NGROK-URL.ngrok.io/tools/update-status`
- **Method**: POST
- **Parameters**:
```json
{
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
}
```

---

## 📞 Step 6: Connect Twilio (For Phone Calls)

Follow the detailed guide in `TWILIO_SETUP.md`, but here's the quick version:

1. **Create Twilio Account**: https://www.twilio.com/try-twilio
2. **Get Credentials**: Copy Account SID and Auth Token
3. **Buy Phone Number**: ~$1/month for local number
4. **Connect in ElevenLabs**:
   - Go to agent settings → Telephony
   - Click "Connect Twilio"
   - Paste Account SID and Auth Token
   - Select your phone number

ElevenLabs will automatically configure everything!

---

## 🧪 Step 7: Test Everything

### Test 1: Backend API

```bash
# Test get_case_details
curl -X POST http://localhost:8000/tools/get-case-details \
  -H "Content-Type: application/json" \
  -d '{"phone": "+15551234567"}'

# Should return debt info for María González
```

### Test 2: Make a Test Call

1. In ElevenLabs, go to your agent
2. Click **"Test Call"** or **"Make Call"**
3. Enter test number: `+15551234567`
4. Click **Start Call**
5. Answer and interact with Jess!

### What Should Happen:

1. ✅ Jess greets you: "Hello, how are you? This is Jess..."
2. ✅ Jess asks for identity confirmation
3. ✅ Jess calls `get_case_details` tool
4. ✅ Jess presents the debt information
5. ✅ Jess offers payment options
6. ✅ Jess calls `update_status` at the end

### Check Database After Call:

Go to Supabase → Table Editor → customers table
- Verify the `status` field updated
- Check `updated_at` timestamp changed

---

## 🎯 Quick Command Reference

```bash
# Start backend
uvicorn main:app --reload

# Start ngrok (in another terminal)
ngrok http 8000

# Test health endpoint
curl http://localhost:8000/health

# Test tool endpoint
curl -X POST http://localhost:8000/tools/get-case-details \
  -H "Content-Type: application/json" \
  -d '{"phone": "+15551234567"}'

# View logs
# Just watch the terminal where uvicorn is running
```

---

## ⚠️ Common Issues

### "Missing required environment variables"
→ Make sure `.env` file has Supabase credentials

### "Customer not found"
→ Run `python seed_data.py` to create test data

### "Connection refused" from ElevenLabs
→ Make sure ngrok is running and URL is correct in tools

### "Tool call failed"
→ Check FastAPI logs in terminal for errors

---

## 📊 Current Status

- ✅ ElevenLabs agent configured
- ✅ API key and Agent ID saved
- ⏳ **NEXT**: Add Supabase credentials to `.env`
- ⏳ **NEXT**: Setup database with `setup_db.py`
- ⏳ **NEXT**: Start backend and ngrok
- ⏳ **NEXT**: Configure tools in ElevenLabs
- ⏳ **NEXT**: Connect Twilio for phone calls

---

## 🎉 You're Almost There!

Just complete steps 1-5 above and you'll be ready to make your first call with Jess!

For detailed help, see:
- `README.md` - Complete documentation
- `TWILIO_SETUP.md` - Twilio integration guide
- `QUICKSTART.md` - Quick reference

**Good luck! 🚀**
