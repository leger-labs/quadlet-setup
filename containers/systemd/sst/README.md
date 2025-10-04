# Faster Whisper STT - Speech-to-Text Service

## Overview

Faster Whisper Server provides OpenAI-compatible speech-to-text transcription using optimized Whisper models. It's integrated with OpenWebUI for audio transcription capabilities.

## Architecture

- **Container**: `sst`
- **Network**: `llm.network` (10.89.0.0/24)
- **Internal Port**: 8000
- **Published Port**: 8000 (for Caddy proxy)
- **Image**: `docker.io/fedirz/faster-whisper-server:latest-cpu`

## Service Communication

SST is accessed by OpenWebUI and other services for speech transcription:

```
OpenWebUI → http://sst:8000
```

External access via Caddy:
```
https://sst.hostname.tailnet.ts.net → localhost:8000 → sst:8000
```

## Configuration

The service uses the Whisper `base` model by default for CPU-optimized performance. Model files are cached in a persistent volume.

### Environment Variables

- `WHISPER_MODEL`: Model size (tiny, base, small, medium, large)
- `WHISPER_LANGUAGE`: Default language code (en, es, fr, etc.)

## Usage

Referenced in OpenWebUI environment as:
```bash
AUDIO_STT_ENGINE=openai
AUDIO_STT_OPENAI_API_BASE_URL=http://sst:8000/v1
```

## API Endpoints

- `POST /v1/audio/transcriptions` - Transcribe audio to text
- `GET /health` - Health check endpoint

## Performance Notes

- Using CPU-optimized image for AMD hardware compatibility
- Base model provides good balance of speed and accuracy
- Models are downloaded on first use and cached locally
- Consider upgrading to `small` or `medium` model for better accuracy
