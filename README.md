# Omi AI Transcript System

A Flask application that receives real-time transcripts from your Omi Dev Kit 2 device, stores them in PostgreSQL, and creates an ongoing AI conversation using OpenAI GPT-5.

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
OMI_API_KEY=your_omi_api_key
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/omi-link
OPENAI_API_KEY=your_openai_api_key
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

- Speak near your Omi device
- Watch your console for incoming transcripts
- You should see detailed output for each webhook received

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

### 4. Configure Environment Variables on Railway

1. In your Railway project, go to "Variables"
2. Add your environment variables:
   - `OMI_API_KEY`: Your Omi API key

### 5. Get Your Railway URL

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
3. **If transcripts found** → Batched and sent to OpenAI GPT-5 with conversation history
4. **AI responds** → Both user message and AI response saved to `messages` table
5. **Transcripts marked as processed** and linked to their message

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

### Every 10 seconds (if new transcripts):
```
============================================================
PROCESSING 2 NEW TRANSCRIPT(S)
============================================================

SENDING TO AI:
------------------------------------------------------------
Previous conversation:
User: Hello
Assistant: Hi there! How can I help you?

User just said:
SPEAKER_1: What's the weather like today?
============================================================

AI RESPONSE:
------------------------------------------------------------
I'm an AI assistant and don't have access to real-time weather 
data, but I'd be happy to help you find that information!
============================================================

Saved user message (ID: 3)
Saved ai message (ID: 4)
Marked 2 transcripts as processed
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

## Project Structure

```
omi-link/
├── app.py                      # Flask web server, webhook receiver
├── db.py                       # PostgreSQL database operations
├── ai_handler.py               # OpenAI GPT-5 API integration
├── transcript_processor.py     # Background polling (10s interval)
├── schema.sql                  # Database table definitions
├── requirements.txt            # Python dependencies
├── Procfile                    # Railway deployment config
├── ENV_TEMPLATE.txt            # Environment variable template
├── SETUP_INSTRUCTIONS.md       # Detailed setup guide
├── .env                        # Your secrets (not committed)
├── .gitignore                  # Git ignore rules
├── database.py                 # OLD: JSON-based (deprecated)
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
- AI messages: GPT-5 responses

## License

MIT License

