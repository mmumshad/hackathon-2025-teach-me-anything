# TechMeAnything Backend

FastAPI backend for the TechMeAnything educational platform.

## Setup

1. **Activate virtual environment:**
   ```bash
   source venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   - Copy `../backend.env` to `.env`
   - Add your actual API keys

4. **Run the server:**
   ```bash
   python main.py
   ```

## API Endpoints

- `GET /` - Root endpoint
- `GET /health` - Health check
- `POST /auth/user` - Create/update user profile
- `POST /chat` - Chat with AI
- `POST /generate-video` - Generate educational video

## Environment Variables

- `OPENAI_API_KEY` - OpenAI API key for LLM
- `ELEVENLABS_API_KEY` - ElevenLabs API key for TTS
- `GEMINI_API_KEY` - Gemini API key for video generation
- `MEM0_API_KEY` - Mem0 API key for user storage

## Development

The server runs on `http://localhost:8000` by default.

API documentation available at `http://localhost:8000/docs`
