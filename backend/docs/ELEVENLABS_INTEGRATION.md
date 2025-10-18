# ElevenLabs Text-to-Speech Integration Guide

## Overview
This guide explains how to integrate ElevenLabs Text-to-Speech API into the TechMeAnything project for generating high-quality audio responses.

## Prerequisites

### 1. ElevenLabs Account Setup
1. Go to [ElevenLabs.io](https://elevenlabs.io/) and create an account
2. Navigate to your profile settings
3. Generate an API key from the API section
4. Add the API key to your `.env` file:

```bash
ELEVENLABS_API_KEY=your_api_key_here
```

### 2. API Key Location
The API key can be found at: [ElevenLabs API Keys](https://elevenlabs.io/app/settings/api-keys)

## Implementation Details

### Service Architecture
The ElevenLabs integration is implemented in `backend/services/elevenlabs_service.py` with the following features:

- **Text-to-Speech Generation**: Convert text responses to high-quality audio
- **Voice Management**: Support for multiple voices and voice selection
- **Educational Optimization**: Voice settings optimized for educational content
- **Error Handling**: Comprehensive error handling and fallback mechanisms

### Key Features

#### 1. Audio Generation
```python
# Generate audio from text
audio_base64 = await elevenlabs_service.generate_audio(text, voice_id)
```

#### 2. Voice Settings
The service includes optimized voice settings for different content types:

**Educational Content:**
- Stability: 0.75 (balanced for clarity)
- Clarity: 0.9 (high clarity for learning)
- Similarity Boost: 0.8 (consistent voice)

**Storytelling Content:**
- Stability: 0.6 (more variation)
- Clarity: 0.85 (expressive but clear)
- Similarity Boost: 0.7 (more natural variation)

#### 3. Voice Management
- List available voices: `GET /api/v1/voices`
- Find voice by name: `get_voice_by_name()`
- Default voice: Rachel (ID: `21m00Tcm4TlvDq8ikWAM`)

## API Endpoints

### 1. Chat Message with Audio
```http
POST /api/v1/chat/message
Content-Type: application/json
X-User-ID: your-user-id

{
  "message": {
    "id": "msg-123",
    "userId": "user-123",
    "content": "Explain photosynthesis to me",
    "timestamp": "2024-01-01T00:00:00Z"
  },
  "requireAudio": true
}
```

**Response:**
```json
{
  "responses": [
    {
      "id": "resp-123",
      "messageId": "msg-123",
      "content": "Photosynthesis is the process...",
      "timestamp": "2024-01-01T00:00:01Z",
      "audioUrl": "data:audio/mpeg;base64,/9j/4AAQSkZJRgABAQAAAQ...",
      "videoUrl": null,
      "quiz": null
    }
  ]
}
```

### 2. Get Available Voices
```http
GET /api/v1/voices
```

**Response:**
```json
{
  "success": true,
  "voices": [
    {
      "voice_id": "21m00Tcm4TlvDq8ikWAM",
      "name": "Rachel",
      "category": "premade",
      "description": "A calm, warm voice perfect for educational content"
    }
  ],
  "count": 1
}
```

### 3. Test Audio Generation
```http
POST /api/v1/audio/generate?text=Hello world&voice_id=21m00Tcm4TlvDq8ikWAM
```

**Response:**
```json
{
  "success": true,
  "audio": "data:audio/mpeg;base64,/9j/4AAQSkZJRgABAQAAAQ...",
  "message": "Audio generated successfully"
}
```

## Usage Examples

### 1. Basic Chat with Audio
```python
import requests

# Send a chat message requesting audio
response = requests.post(
    "http://localhost:8000/api/v1/chat/message",
    headers={
        "Content-Type": "application/json",
        "X-User-ID": "test-user"
    },
    json={
        "message": {
            "id": "msg-1",
            "userId": "test-user",
            "content": "Can you explain gravity in simple terms?",
            "timestamp": "2024-01-01T00:00:00Z"
        },
        "requireAudio": True
    }
)

data = response.json()
audio_url = data["responses"][0]["audioUrl"]
print(f"Audio URL: {audio_url}")
```

### 2. Frontend Integration
```javascript
// Fetch chat response with audio
const response = await fetch('/api/v1/chat/message', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-User-ID': userId
  },
  body: JSON.stringify({
    message: {
      id: generateId(),
      userId: userId,
      content: userMessage,
      timestamp: new Date().toISOString()
    },
    requireAudio: true
  })
});

const data = await response.json();
const audioUrl = data.responses[0].audioUrl;

// Play audio if available
if (audioUrl) {
  const audio = new Audio(audioUrl);
  audio.play();
}
```

## Voice Selection

### Recommended Voices for Education
1. **Rachel** (`21m00Tcm4TlvDq8ikWAM`) - Calm, warm voice
2. **Drew** (`29vD33N1CtxCmqQRPOHJ`) - Clear, professional
3. **Clyde** (`2EiwWnXFnvU5JabPnv8n`) - Friendly, approachable

### Finding Voice IDs
```python
# Get all available voices
voices = await elevenlabs_service.get_available_voices()
for voice in voices['voices']:
    print(f"Name: {voice['name']}, ID: {voice['voice_id']}")
```

## Error Handling

The service includes comprehensive error handling:

- **API Key Missing**: Graceful fallback to mock audio URLs
- **Network Timeouts**: 30-second timeout with retry logic
- **API Errors**: Detailed error logging and fallback mechanisms
- **Invalid Voice IDs**: Default voice fallback

## Performance Considerations

### Audio Storage
Currently, audio is returned as base64 data URLs. For production:

1. **File Storage**: Save audio files to cloud storage (AWS S3, etc.)
2. **CDN**: Use CDN for faster audio delivery
3. **Caching**: Cache frequently requested audio content

### Optimization Tips
1. **Text Length**: Shorter texts generate faster
2. **Voice Selection**: Some voices are faster than others
3. **Caching**: Cache audio for repeated content
4. **Async Processing**: Generate audio asynchronously when possible

## Troubleshooting

### Common Issues

1. **"ElevenLabs API key not found"**
   - Check your `.env` file has `ELEVENLABS_API_KEY`
   - Restart the server after adding the key

2. **"Failed to generate audio"**
   - Verify your API key is valid
   - Check your ElevenLabs account credits
   - Ensure network connectivity

3. **Slow audio generation**
   - Reduce text length
   - Use faster voice models
   - Implement caching

### Debug Mode
Enable debug logging by setting:
```bash
DEBUG=true
```

## Cost Optimization

### ElevenLabs Pricing
- Free tier: 10,000 characters/month
- Paid plans: $5/month for 30,000 characters
- Enterprise: Custom pricing

### Optimization Strategies
1. **Text Preprocessing**: Remove unnecessary text
2. **Smart Caching**: Cache common responses
3. **User Preferences**: Let users choose audio quality
4. **Lazy Loading**: Generate audio on-demand

## Security Considerations

1. **API Key Protection**: Never expose API keys in client-side code
2. **Rate Limiting**: Implement rate limiting for audio generation
3. **Input Validation**: Validate text input before sending to API
4. **Content Filtering**: Filter inappropriate content before audio generation

## Future Enhancements

1. **Voice Cloning**: Custom voice creation for branded content
2. **Multi-language Support**: Support for 29+ languages
3. **Real-time Streaming**: Streaming audio generation
4. **Voice Effects**: Emotional tone adjustments
5. **Batch Processing**: Multiple audio generation in single request

