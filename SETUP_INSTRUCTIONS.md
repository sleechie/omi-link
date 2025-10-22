# Setup Instructions for Omi AI Transcript System

## Prerequisites

- Python 3.8+
- PostgreSQL installed and running (pgAdmin4)
- Omi Dev Kit 2 device
- OpenAI API key
- localtunnel (for local testing)

## Step 1: Database Setup

1. Open pgAdmin4
2. Connect to your PostgreSQL server (pnid-local or similar)
3. Create a new database called `omi-link`:
   - Right-click "Databases" → Create → Database
   - Database name: `omi-link`
   - Owner: postgres
   - Click Save

## Step 2: Environment Variables

1. Copy `.env.example` to `.env`:
   ```powershell
   copy .env.example .env
   ```

2. Edit `.env` and add your credentials:
   ```
   OMI_API_KEY=your_omi_api_key
   DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/omi-link
   OPENAI_API_KEY=your_openai_api_key
   ```

   Replace:
   - `YOUR_PASSWORD` with your PostgreSQL password
   - `your_omi_api_key` with your Omi API key from the Omi app
   - `your_openai_api_key` with your OpenAI API key

## Step 3: Install Dependencies

```powershell
pip install -r requirements.txt
```

## Step 4: Initialize Database

The database will be automatically initialized when you first run the app. The `schema.sql` file contains the table definitions.

## Step 5: Start the Application

```powershell
python app.py
```

You should see:
```
Database initialized successfully
TRANSCRIPT PROCESSOR STARTED
Polling every 10 seconds for new transcripts
OMI WEBHOOK RECEIVER STARTING
Server running on port 5000
```

## Step 6: Expose Local Server (for testing)

In a **separate terminal**:

```powershell
npm install -g localtunnel
lt --port 5000
```

You'll get a URL like: `https://abc-123.loca.lt`

## Step 7: Configure Omi Device

1. Open the Omi mobile app
2. Go to Settings > Developer
3. Find webhook configuration
4. Enter your localtunnel URL: `https://abc-123.loca.lt` (without /webhook)
5. Save settings

## Step 8: Test It!

1. Speak near your Omi device
2. Watch the Flask terminal for:
   - Webhook received messages
   - Transcripts saved to database
   - Every 10 seconds: AI processing messages
   - AI responses

## Viewing Conversation

Visit in your browser:
- Health check: `http://localhost:5000/`
- Conversation history: `http://localhost:5000/conversation`

Or with localtunnel:
- `https://abc-123.loca.lt/conversation`

## Database Tables

### `transcripts`
Stores all incoming transcript segments from Omi device:
- Individual speech segments
- Speaker identification
- Timestamps
- Processing status
- Linked to messages

### `messages`
Stores the conversation:
- User messages (batched transcripts every 10 seconds)
- AI responses
- Timestamps

## Troubleshooting

### "DATABASE_URL environment variable not set"
- Make sure you created the `.env` file (not just `.env.example`)
- Verify the DATABASE_URL is correctly formatted

### "Could not initialize database"
- Check PostgreSQL is running
- Verify database name and password in DATABASE_URL
- Make sure `omi-link` database exists in pgAdmin

### "ERROR calling OpenAI API"
- Verify your OPENAI_API_KEY is correct
- Make sure you have API credits
- Check you have access to GPT-5 API

### No transcripts being processed
- Check Omi device is connected and sending webhooks
- Verify localtunnel is running
- Check webhook URL in Omi app settings

### Polling too fast/slow
The default is 10 seconds. To change it temporarily:
```python
# In Python console or add to app.py
import transcript_processor
transcript_processor.set_poll_interval(5)  # 5 seconds for testing
```

## Architecture Overview

```
Omi Device
    ↓ (webhook)
Flask App (app.py)
    ↓
Database (transcripts table)
    ↓ (every 10 seconds)
Transcript Processor (transcript_processor.py)
    ↓
AI Handler (ai_handler.py)
    ↓
OpenAI GPT-5 API
    ↓
Database (messages table)
```

## Production Deployment (Railway)

1. Push to GitHub
2. Connect Railway to your repo
3. Add environment variables in Railway dashboard:
   - `OMI_API_KEY`
   - `DATABASE_URL` (Railway will provide PostgreSQL)
   - `OPENAI_API_KEY`
4. Deploy
5. Update Omi webhook URL to Railway URL

## Files Overview

- `app.py` - Flask web server, receives webhooks
- `db.py` - Database operations (PostgreSQL)
- `ai_handler.py` - OpenAI API integration
- `transcript_processor.py` - Background polling thread
- `schema.sql` - Database schema
- `requirements.txt` - Python dependencies
- `Procfile` - Railway deployment config

