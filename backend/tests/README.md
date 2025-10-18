# 🧪 Tests Directory

This directory contains test scripts for the TechMeAnything backend services.

## 📁 Test Files

### `test_openai_video.py`
- **Purpose**: Basic test of OpenAI video service
- **Features**: Service initialization, parameter validation, video listing
- **Usage**: `python test_openai_video.py`

### `test_planets_video.py`
- **Purpose**: Comprehensive test with real video generation
- **Features**: Creates educational planets video, waits for completion, downloads
- **Usage**: `python test_planets_video.py`

## 🚀 Running Tests

From the backend directory:

```bash
# Run individual tests
python tests/test_openai_video.py
python tests/test_planets_video.py

# Or from the tests directory
cd tests
python test_openai_video.py
python test_planets_video.py
```

## 📋 Test Requirements

- **OpenAI API Key**: Required for video generation tests
- **Internet Connection**: Required for API calls

## 🎯 Test Coverage

- ✅ **Video Generation**: OpenAI Sora 2 integration
- ✅ **Status Checking**: Video progress monitoring
- ✅ **Video Download**: File download and storage
- ✅ **Error Handling**: API error scenarios
- ✅ **Parameter Validation**: Input validation
- ✅ **Educational Content**: Real-world usage examples

## 📝 Notes

- Tests create real videos using OpenAI Sora 2
- Videos are saved to `../downloads/` directory
- Some tests may take several minutes to complete
- Check API credits before running extensive tests
