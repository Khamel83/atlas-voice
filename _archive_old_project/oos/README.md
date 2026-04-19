# 🎭 OOS Voice Integration System

A comprehensive voice profile integration system that enables context-aware, adaptive AI communication that sounds authentically like you.

## 🚀 Quick Start

### Using Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/Khamel83/oos.git
cd oos

# Start the system
docker-compose up -d

# Access the dashboard
# Web Dashboard: http://localhost:8080
# API Documentation: http://localhost:8000/docs
```

### Manual Installation

```bash
# Install dependencies
pip install -r requirements.txt
pip install fastapi uvicorn

# Start the API server
uvicorn src.voice_api:app --reload --host 0.0.0.0 --port 8000

# Open the web dashboard
open web/dashboard.html
```

## 🎯 Core Features

### Voice Profiles
- **6-Tier Voice Stratification**: OMAR_BASE, OMAR_TECH, OMAR_CASUAL, OMAR_PRO, OMAR_ANALYSIS, OMAR_CREATIVITY
- **Context-Aware Adaptation**: Automatic voice switching based on conversation context
- **Real-time Learning**: Machine learning engine that improves based on user feedback

### Voice Commands
- `/voice-list` - List available voice profiles
- `/voice-use [profile]` - Switch voice profile
- `/voice-context [type]` - Set context manually
- `/voice-analyze [text]` - Analyze text for voice characteristics
- `/voice-stats` - Show usage statistics

### Enhanced Workflows
- **Voice Planning**: Create project plans in your authentic voice
- **Voice Writing**: Generate content that sounds like you
- **Voice Analysis**: Analyze data with your analytical style
- **Voice Debugging**: Debug technical issues in your voice
- **Voice Documentation**: Create professional documentation

### Session Management
- **Multi-session Support**: Manage multiple voice sessions simultaneously
- **Session Persistence**: Voice sessions persist across restarts
- **Activity Tracking**: Complete audit trail of voice adaptations

## 📊 API Documentation

### Core Endpoints

#### Voice Profile Management
```bash
GET  /api/voice/profiles              # List all voice profiles
POST /api/voice/select               # Select active profile
GET  /api/voice/current              # Get current profile info
POST /api/voice/generate-prompt      # Generate AI prompt
GET  /api/voice/export/{profile}     # Export profile data
```

#### Context Detection & Adaptation
```bash
POST /api/voice/detect-context       # Detect context from text
POST /api/voice/adapt               # Adapt voice to context
```

#### Commands & Workflows
```bash
POST /api/voice/command              # Execute voice command
GET  /api/voice/commands            # List available commands
POST /api/voice/workflow             # Execute voice workflow
GET  /api/voice/workflows            # List available workflows
```

#### Session Management
```bash
POST /api/voice/sessions             # Create new session
GET  /api/voice/sessions/{id}        # Get session info
POST /api/voice/sessions/{id}/switch # Switch voice in session
DELETE /api/voice/sessions/{id}      # End session
```

#### Analytics & Insights
```bash
GET  /api/voice/analytics            # Get usage analytics
GET  /api/voice/engine/state        # Get engine state
POST /api/voice/feedback            # Submit feedback
POST /api/voice/optimize            # Optimize adaptation engine
```

### Example API Usage

```bash
# Create a session
curl -X POST "http://localhost:8000/api/voice/sessions" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "demo_user"}'

# Switch voice profile
curl -X POST "http://localhost:8000/api/voice/select" \
  -H "Content-Type: application/json" \
  -d '{"profile_name": "OMAR_TECH"}'

# Detect context and adapt
curl -X POST "http://localhost:8000/api/voice/adapt" \
  -H "Content-Type: application/json" \
  -d '{"context_type": "technical", "input_text": "Let me explain this database system"}'

# Execute workflow
curl -X POST "http://localhost:8000/api/voice/workflow" \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_type": "voice_planning",
    "input_data": {"task": "implement user authentication", "complexity": "medium"}
  }'
```

## 🎭 Voice Profile Details

### OMAR_BASE (Default)
- **Description**: Your authentic, balanced communication style
- **Characteristics**: Collaborative, conversational academic, slight positive bias
- **Key Phrases**: "basically", "like", "just", "actually", "you know"
- **Use Cases**: General communication, default setting

### OMAR_TECH
- **Description**: Technical but accessible explanations
- **Characteristics**: Technical collaborative, higher formality, moderate technical level
- **Key Phrases**: "basically", "like", "implementation", "system", "architecture"
- **Use Cases**: Technical documentation, code explanation, system design

### OMAR_CASUAL
- **Description**: Friend-to-friend conversational style
- **Characteristics**: Casual direct, informal, high enthusiasm
- **Key Phrases**: "like", "just", "you know", "man", "actually"
- **Use Cases**: Social media, personal emails, casual conversation

### OMAR_PRO
- **Description**: Professional correspondence style
- **Characteristics**: Professional collaborative, high formality, moderate enthusiasm
- **Key Phrases**: "regarding", "following up", "basically", "implementation"
- **Use Cases**: Business communication, formal documentation, client emails

### OMAR_ANALYSIS
- **Description**: Deep analytical writing style
- **Characteristics**: Analytical academic, very formal, high technical level
- **Key Phrases**: "analysis", "research", "basically", "implementation", "system"
- **Use Cases**: Academic papers, data analysis, research documentation

### OMAR_CREATIVITY
- **Description**: Creative/brainstorming mode
- **Characteristics**: Creative divergent, low formality, very high enthusiasm
- **Key Phrases**: "ideas", "brainstorm", "basically", "like", "what if"
- **Use Cases**: Brainstorming, creative writing, ideation

## 🔧 Configuration

### Environment Variables

```bash
# Database Configuration
DATABASE_URL=sqlite:///tmp/voice_sessions.db

# Voice Profile Configuration
VOICE_PROFILE_PATH=/path/to/voice-profile
DEFAULT_VOICE_PROFILE=OMAR_BASE

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=*

# Adaptation Engine Configuration
LEARNING_RATE=0.1
CONFIDENCE_THRESHOLD=0.7
ADAPTATION_WINDOW=300

# Session Management
SESSION_TIMEOUT=3600
MAX_SESSIONS=1000
```

### Voice Profile Customization

Voice profiles can be customized by modifying the characteristics in `src/oos_voice_engine.py`:

```python
self.profiles[VoiceProfile.OMAR_BASE] = VoiceProfileData(
    profile_id="OMAR_BASE",
    description="Your custom description",
    characteristics=VoiceCharacteristics(
        communication_style="your_style",
        key_phrases=["your", "phrases", "here"],
        sentence_length=12.8,
        formality=0.3,
        positivity=0.11,
        technical_level=0.06,
        enthusiasm=0.45,
        directness=0.72
    ),
    # ... other configuration
)
```

## 📈 Performance Metrics

### Success Criteria
- **Voice Accuracy**: >85% user-perceived similarity
- **Context Detection**: >90% accuracy
- **Performance**: <100ms voice switching latency
- **Reliability**: 99.9% uptime
- **User Satisfaction**: >80% positive feedback

### System Performance
- **Response Time**: <50ms for API calls
- **Memory Usage**: <100MB per session
- **Concurrent Users**: 1000+ simultaneous sessions
- **Database**: SQLite for development, PostgreSQL for production

## 🧪 Testing

### Unit Tests
```bash
# Test individual components
python -m pytest tests/ -v
```

### Integration Tests
```bash
# Test API endpoints
python -m pytest tests/api/ -v

# Test voice workflows
python -m pytest tests/workflows/ -v
```

### Performance Tests
```bash
# Load testing
locust -f tests/locustfile.py

# Performance benchmarking
python tests/performance.py
```

## 🚀 Deployment

### Production Deployment

1. **Environment Setup**
```bash
# Set up production environment
export NODE_ENV=production
export DATABASE_URL=postgresql://user:pass@localhost/voice_oos
```

2. **Docker Deployment**
```bash
# Build and deploy
docker-compose -f docker-compose.prod.yml up -d
```

3. **Kubernetes Deployment**
```bash
# Deploy to Kubernetes
kubectl apply -f k8s/
```

### Monitoring Setup

- **Health Checks**: `/health` endpoint
- **Metrics**: `/api/voice/analytics` endpoint
- **Logging**: Structured logging with timestamps
- **Alerting**: Configurable alerts for system health

## 🔒 Security

### Authentication
- API key authentication (optional)
- JWT tokens for user sessions
- Rate limiting on API endpoints

### Data Privacy
- Local data storage by default
- Optional encryption for sensitive data
- GDPR compliance features

### API Security
- CORS configuration
- Input validation and sanitization
- SQL injection prevention
- XSS protection

## 📚 Documentation

- [API Documentation](http://localhost:8000/docs) - Interactive API docs
- [Voice Profile Guide](docs/voice-profiles.md) - Detailed profile configuration
- [Integration Guide](docs/integration.md) - How to integrate with existing systems
- [Deployment Guide](docs/deployment.md) - Production deployment instructions

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

Built with ❤️ using your authentic voice profile data and communication patterns.

---

**Note**: This system is designed to work seamlessly with your existing OOS middleware and provides a complete voice enhancement layer for all your AI interactions.
