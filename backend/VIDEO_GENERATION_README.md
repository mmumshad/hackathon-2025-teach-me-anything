# 🎬 Video Generation Module

A simple and beginner-friendly video generation service for the TechMeAnything project! This module uses OpenAI Sora 2 for video generation.

## 📁 What's Included

- **`openai_video_service.py`** - OpenAI Sora 2 video generation service
- **Simple and focused** - Only OpenAI Sora 2, no complexity

## 🚀 Quick Start

### 1. Setup API Keys

Create a `.env` file in the backend folder and add your API key:

```env
# Required for OpenAI Sora 2
OPENAI_API_KEY=your_openai_api_key_here
```

### 2. Install Dependencies

The required dependencies are already in `requirements.txt`:
- `openai` - For OpenAI API integration

### 3. Use the Service

```python
from services.openai_video_service import OpenAIVideoService

# Create service
service = OpenAIVideoService()

# Generate video
result = await service.generate_video("A cat playing piano")
```

## 🎯 How It Works

### Basic Usage

```python
from services.openai_video_service import OpenAIVideoService

# Create the service
video_service = OpenAIVideoService()

# Generate a video
result = await video_service.generate_video("A cat playing with yarn")

# Check status
status = await video_service.check_status(result['id'])

# Wait for completion
final_result = await video_service.wait_for_completion(result['id'])
```

### Available Methods

#### Generate Videos
- `generate_video(prompt)` - Generate video with OpenAI Sora 2

#### Check Status
- `check_status(video_id)` - Check video generation status
- `wait_for_completion(video_id)` - Wait until video is ready

#### Download & List
- `download_video(video_id)` - Download completed video
- `list_videos()` - List all generated videos

## 🔧 Configuration

The service automatically reads configuration from your `config.py` file:

- **OPENAI_API_KEY** - Your OpenAI API key

## 📝 Example Prompts

Here are some fun prompts to try:

- "A majestic dragon soaring through clouds above a fantasy castle"
- "A golden retriever playing in the snow with children"
- "A futuristic city with flying cars and neon lights"
- "A peaceful garden with butterflies and flowers"
- "A cooking tutorial showing how to make pasta"

## ⚠️ Important Notes

### OpenAI Sora 2
- **Currently available** - Real API is working!
- **Requires API access** - Need proper OpenAI API key with video permissions
- **Uses OpenAI's Python SDK** - Direct integration with OpenAI

## 🐛 Troubleshooting

### Common Issues

1. **"API key not found"**
   - Make sure your `.env` file is in the backend folder
   - Check that the API key names match exactly

2. **"Service not available"**
   - Verify your API keys are valid
   - Check if you have video generation permissions

3. **"Video generation failed"**
   - Check your API credits/limits
   - Try a simpler prompt
   - Verify internet connection

### Getting Help

- Check the service output for detailed error messages
- Make sure you're running scripts from the backend directory

## 🎓 Learning Path

For beginners (like Mumshad! 😊):

1. **Import the service** - `from services.openai_video_service import OpenAIVideoService`
2. **Try different prompts** - Experiment with your own ideas
3. **Read the code** - Understand how it's built
4. **Add to your app** - Integrate into your main project

## 🔮 Future Enhancements

- Video download and storage
- Batch video generation
- Video editing and processing
- Integration with the main TechMeAnything API

---

Happy video generating! 🎬✨
