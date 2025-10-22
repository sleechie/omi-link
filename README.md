# Omi AI Transcript System - Jarvis

A Flask application that receives real-time transcripts from your Omi Dev Kit 2 device, stores them in PostgreSQL, and creates an ongoing AI conversation with **Jarvis** - your personal AI assistant powered by OpenAI Agents SDK.

## Features

- 🎤 **Real-time Transcript Processing** - Receives webhooks from Omi device every 10 seconds
- 🤖 **Jarvis AI Assistant** - Powered by OpenAI GPT-5 with persistent conversation memory
- 🔍 **Web Search** - Jarvis can search the web for current information (weather, news, etc.)
- 📱 **SMS Notifications** - All AI responses are automatically texted to your phone
- 💾 **Persistent Sessions** - Conversations persist across restarts using OpenAI Conversations API
- 🎯 **Activation Phrases** - Only activates when you say "Hey Jarvis" (and variations)
- 🧠 **Context Aware** - Remembers previous conversations per device

## Quick Setup

### 1. Database Setup

1. Open pgAdmin4 and connect to your PostgreSQL server
2. Create a database named `omi-link`

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Environment Variables

Copy `ENV_TEMPLATE.txt` to `.env` and fill in your credentials:

```
# Omi Device API Key (optional for webhooks)
OMI_API_KEY=your_omi_api_key

# PostgreSQL Database Connection
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/omi-link

# OpenAI API Key (for Jarvis AI)
OPENAI_API_KEY=your_openai_api_key

# Phone Number for SMS notifications (10-digit US format)
PHONE_NUMBER=5555555555

# Textbelt API Key (use 'textbelt' for free tier with 1 text/day)
# Get a paid key at https://textbelt.com for unlimited texts
TEXTBELT_API_KEY=textbelt

# Flask Environment
FLASK_ENV=development
```

**See `SETUP_INSTRUCTIONS.md` for detailed setup guide.**

### 4. Run the Application

```bash
python app.py
```

The server will start on `http://localhost:5000` and automatically:
- Initialize the PostgreSQL database
- Start the transcript processor (polls every 10 seconds)
- Begin receiving webhooks from your Omi device

## Testing Locally with ngrok

Since your Omi device needs to send webhooks to a public URL, you'll need to use ngrok to expose your local server:

### 1. Install ngrok

Download from [ngrok.com](https://ngrok.com) or install via:

```bash
# Windows (using Chocolatey)
choco install ngrok

# Or download the executable directly from ngrok.com
```

### 2. Start ngrok

In a new terminal window:

```bash
ngrok http 5000
```

You'll see output like:
```
Forwarding    https://abc123.ngrok.io -> http://localhost:5000
```

### 3. Configure Your Omi Device

In the Omi mobile app:
1. Go to Settings > Developer
2. Find the webhook configuration section
3. Enter your ngrok URL + `/webhook`:
   ```
   https://abc123.ngrok.io/webhook
   ```

### 4. Test It Out

**Option 1: With Omi Device**
- Speak near your Omi device: "Hey Jarvis, what's the weather today?"
- Watch your console for incoming transcripts and AI processing
- Check your phone for SMS response from Jarvis

**Option 2: Local Testing Script**
```bash
# Single message test
python dev/test_jarvis.py "Hey Jarvis, what time is it?"

# Interactive mode (continuous conversation)
python dev/test_jarvis.py
```

## Deploying to Railway

### 1. Initialize Git Repository (if not already done)

```bash
git init
git add .
git commit -m "Initial commit: Omi webhook receiver"
```

### 2. Create GitHub Repository

1. Create a new repository on GitHub
2. Push your code:

```bash
git remote add origin https://github.com/yourusername/omi-link.git
git branch -M main
git push -u origin main
```

### 3. Deploy to Railway

1. Go to [railway.app](https://railway.app)
2. Sign up/login with GitHub
3. Click "New Project" > "Deploy from GitHub repo"
4. Select your `omi-link` repository
5. Railway will automatically detect the Flask app and deploy it

### 4. Add PostgreSQL Database

1. In your Railway project, click "New"
2. Select "Database" > "PostgreSQL"
3. Railway will automatically create `DATABASE_URL` variable

### 5. Configure Environment Variables on Railway

1. In your Railway project, go to "Variables"
2. Add your environment variables:
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `PHONE_NUMBER`: Your 10-digit phone number
   - `TEXTBELT_API_KEY`: Your Textbelt API key (or 'textbelt' for free tier)
   - `OMI_API_KEY`: Your Omi API key (optional)

### 6. Get Your Railway URL

1. Once deployed, Railway will give you a URL like:
   ```
   https://your-app-name.up.railway.app
   ```
2. Update your Omi device webhook URL to:
   ```
   https://your-app-name.up.railway.app/webhook
   ```

## How It Works

1. **Omi Device sends webhooks** → Transcripts saved to PostgreSQL `transcripts` table
2. **Every 10 seconds**, background processor checks for new transcripts
3. **Activation phrase check** → Only processes if transcript contains "hey jarvis" (or variations)
4. **Session management** → Retrieves or creates OpenAI Conversation session for this Omi device
5. **Jarvis processes** → OpenAI Agents SDK automatically:
   - Loads conversation history from OpenAI
   - Performs web searches if needed
   - Can send additional SMS during processing
6. **Response handling** → AI response is automatically texted to your phone
7. **Database updates** → User message and AI response saved to `messages` table
8. **Session persistence** → Conversation ID saved for future interactions

## API Endpoints

### `GET /`
Health check endpoint. Returns server status.

### `POST /webhook`
Receives webhook data from Omi device. Automatically saves transcript segments to database.

### `GET /conversation`
Returns the complete conversation history:
```json
{
  "status": "success",
  "count": 10,
  "messages": [
    {
      "id": 1,
      "message_type": "user",
      "message_text": "SPEAKER_1: Hello there",
      "timestamp": "2025-10-21T21:30:00"
    },
    {
      "id": 2,
      "message_type": "ai",
      "message_text": "Hello! How can I help you?",
      "timestamp": "2025-10-21T21:30:05"
    }
  ]
}
```

## Console Output Example

### When webhook is received:
```
============================================================
NEW WEBHOOK RECEIVED - 2025-10-21 21:30:00
============================================================

Transcript Segments: 2 segment(s)
------------------------------------------------------------

Segment 1:
  Speaker: SPEAKER_1
  Time: 0.00s - 2.50s
  Text: What's the weather like today?

Saved transcript segment abc-123 to database
============================================================
```

### Every 10 seconds (if new transcripts with activation phrase):
```
============================================================
PROCESSING 2 NEW TRANSCRIPT(S)
============================================================
Activation phrase 'hey jarvis' detected!

Creating new conversation for Omi session device_abc123

============================================================
SENDING TO JARVIS (with Agents SDK):
------------------------------------------------------------
SPEAKER_1: Hey Jarvis, what's the weather like today?
============================================================

[Jarvis uses web search tool to find current weather]

============================================================
JARVIS RESPONSE:
------------------------------------------------------------
It's currently 72°F and sunny in San Francisco.
============================================================

============================================================
SENDING AI RESPONSE VIA SMS
============================================================
Response: It's currently 72°F and sunny in San Francisco.
============================================================

✅ AI response texted successfully! Text ID: 123456

Saved user message (ID: 3)
Saved ai message (ID: 4)
Saved session mapping: device_abc123 -> conv_openai_xyz789
Successfully processed 2 transcript(s)
============================================================
```

## Troubleshooting

### Port Already in Use
If port 5000 is already in use, change it in `app.py` or set the PORT environment variable:
```bash
export PORT=8000
python app.py
```

### No Data Received
- Check that your Omi device is connected to the internet
- Verify the webhook URL in the Omi app settings
- Check ngrok is running if testing locally
- Look for error messages in the console

### Railway Deployment Issues
- Ensure `Procfile` is in the root directory
- Check Railway logs for errors
- Verify environment variables are set correctly
- Add PostgreSQL database service in Railway

### SMS Not Sending
- Verify `PHONE_NUMBER` is in correct format (10 digits for US)
- Check `TEXTBELT_API_KEY` is valid
- Free tier allows 1 text per day - get paid key at textbelt.com
- Test SMS with: `python -c "import sms; sms.send_sms('test')"`

### Jarvis Not Responding
- Ensure you're saying an activation phrase ("hey jarvis")
- Check console for "Activation phrase detected" message
- Verify OpenAI API key is valid
- Check that transcripts contain the activation phrase

## Project Structure

```
omi-link/
├── app.py                      # Flask web server, webhook receiver
├── db.py                       # PostgreSQL database operations
├── ai_handler.py               # Jarvis AI Agent (OpenAI Agents SDK)
├── sessions.py                 # OpenAI Conversations session management
├── tools.py                    # Jarvis tools (@function_tool decorators)
├── sms.py                      # SMS notifications via Textbelt
├── transcript_processor.py     # Background polling (10s interval)
├── schema.sql                  # Database table definitions
├── requirements.txt            # Python dependencies
├── Procfile                    # Railway deployment config
├── ENV_TEMPLATE.txt            # Environment variable template
├── .env                        # Your secrets (not committed)
├── .gitignore                  # Git ignore rules
├── dev/
│   ├── reset_db.py            # Database cleanup utility
│   └── test_jarvis.py         # Local testing script
└── README.md                   # This file
```

## Database Schema

### `transcripts` Table
- Stores individual speech segments from Omi device
- Tracks processing status
- Links to messages

### `messages` Table
- Stores conversation between user and AI
- User messages: batched transcripts
- AI messages: Jarvis responses
- Optional: tool_executions tracking

### `sessions` Table
- Maps Omi device session IDs to OpenAI conversation IDs
- Enables persistent conversation memory
- Tracks last usage timestamps

## Jarvis AI Features

### Activation Phrases
Jarvis only responds when you say one of these phrases:
- "hey jarvis" / "hey, jarvis"
- "hi jarvis" / "hi, jarvis"
- "hello jarvis" / "hello, jarvis"
- "okay jarvis" / "ok jarvis"

### Available Tools

1. **Web Search** - Automatically searches the web for:
   - Current weather
   - News and events
   - Sports scores
   - Stock prices
   - Any real-time information

2. **Send Text Message** - Can send additional SMS during processing:
   - Status updates ("Looking that up...")
   - Multi-part responses
   - Note: Final response is ALWAYS auto-texted

### Conversation Memory

Jarvis remembers your entire conversation history using OpenAI Conversations API:
```
You: "Hey Jarvis, my favorite color is blue"
Jarvis: "Got it, I'll remember that!"

[Later that day...]
You: "Hey Jarvis, what's my favorite color?"
Jarvis: "Your favorite color is blue"
```

Each Omi device has its own conversation thread that persists forever.

## Development & Testing

### Testing Script (`dev/test_jarvis.py`)

Test Jarvis locally without needing webhooks:

**Interactive Mode:**
```bash
python dev/test_jarvis.py
```
- Start a continuous conversation with Jarvis
- Type your messages and press Enter
- Type `new` to start a fresh session
- Type `exit` or `quit` to stop

**Single Message Mode:**
```bash
python dev/test_jarvis.py "Hey Jarvis, what's the weather?"
```
- Send a single message and get a response
- Useful for quick testing

**Note:** The test script bypasses the webhook → transcript processor flow, so:
- ✅ Jarvis will respond
- ✅ Sessions will persist
- ✅ Tools (web search) will work
- ❌ Auto-SMS won't trigger (only in production flow)

### Database Reset Script (`dev/reset_db.py`)

Clear all data from the database:

```bash
python dev/reset_db.py
```

This will:
- Truncate `transcripts` table
- Truncate `messages` table
- Truncate `sessions` table
- Keep the schema intact

## License

MIT License

