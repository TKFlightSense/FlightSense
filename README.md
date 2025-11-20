# FlightSense

AI-Powered Airline Customer Feedback Analysis & Ticketing System

## Overview

FlightSense is an enterprise-grade system that automatically analyzes airline passenger feedback using LLM-based classification, routes issues to appropriate departments via Jira-like tickets, and provides role-based analytics dashboards.

## Key Features

- 🤖 **AI-Powered Classification** - LLM-based segmentation and labeling of passenger feedback
- 🎫 **Automated Ticketing** - Routes feedback to departments (GroundOps, Baggage, Catering, Support)
- 🔐 **Role-Based Access Control** - JWT authentication with department-specific permissions
- 📊 **Analytics Dashboard** - Sentiment analysis, trend tracking, and subtopic distribution
- 📧 **Automated Reports** - Daily email summaries to department teams
- 🔄 **Multi-Provider LLM** - Supports OpenAI and vLLM (local inference)

## Quick Start

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/TKFlightSense/FlightSense.git
cd FlightSense

# Install dependencies
pip install -r requirements.txt

# Install LLM provider (choose one)
pip install openai  # For OpenAI API
# OR
pip install vllm    # For local inference (requires GPU)
```

### 2. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env and set your API keys
# Required: OPENAI_API_KEY, LLM_PROVIDER, LLM_MODEL
```

### 3. Test LLM Setup

```bash
# Run the test suite
python test_llm_setup.py
```

### 4. Initialize Database

```bash
# The database will auto-initialize on first run
# Or manually initialize:
python -c "from services.db_service.db_service import DbService; DbService()"
```

## LLM Integration

FlightSense supports multiple LLM providers:

### OpenAI (Recommended for Getting Started)

```bash
# Install
pip install openai

# Configure
export OPENAI_API_KEY=sk-your-key-here
export LLM_PROVIDER=openai
export LLM_MODEL=gpt-4o-mini
```

### vLLM (For Production/High Volume)

```bash
# Install (requires GPU)
pip install vllm

# Configure
export LLM_PROVIDER=vllm
export LLM_MODEL=meta-llama/Llama-3.1-8B-Instruct
```

See [docs/LLM_SETUP.md](docs/LLM_SETUP.md) for detailed setup instructions.

## Usage Example

```python
from packages.llm.classifier import FeedbackClassifier

# Label and classify feedback
classifier = FeedbackClassifier()
review = "Flight delayed 3 hours. Baggage lost. Food was cold."

# Get labeled segments
segments = classifier.label_review(review)

# Or classify batch for database
df = classifier.classify_batch([review])
print(df[['review', 'labels']])
```

## Project Structure

```
FlightSense/
├── models/              # Data models, labels, roles, enums
├── packages/            # Reusable components
│   ├── llm/            # LLM client, classifier, segmentation
│   ├── stats/          # Statistics and analytics
│   ├── jira_client/    # Jira API wrapper
│   └── tickets/        # Ticket management
├── services/            # Business logic
│   ├── auth_service.py
│   ├── data_service.py
│   ├── reporting_service.py
│   ├── agents/         # Automation agents
│   ├── db_service/     # Database operations
│   └── orchestrator/   # Main orchestrator
├── configs/             # Configuration files
└── docs/               # Documentation
```

## Documentation

- [LLM Setup Guide](docs/LLM_SETUP.md) - Comprehensive LLM configuration
- [LLM Package README](packages/llm/README.md) - API documentation

## Features in Detail

### Fine-Grained Feedback Classification

12 specific categories:
- Inflight experience (food, seats, entertainment, service, cleanliness)
- Check-in and boarding process
- Baggage (lost, damaged)
- Booking and ticketing
- Customer support
- Pricing and loyalty

### Department Routing

Automatic ticket creation and routing:
- **GroundOps**: Check-in, boarding issues
- **Baggage**: Lost/damaged baggage
- **Catering**: Inflight service issues
- **CustomerSupport**: Booking, pricing, general support

### Role-Based Access

User roles:
- `admin` - Full access
- `manager` - Full access with reporting
- `viewer` - Read-only dashboard
- Department roles - Limited to specific categories

## Development

### Run Tests

```bash
# Test LLM integration
python test_llm_setup.py

# Run all tests (if pytest is configured)
pytest
```

### Code Quality

```bash
# Format code
make fmt

# Run linters
make lint
```

## Requirements

- Python 3.10+
- SQLite (included)
- OpenAI API key OR GPU for vLLM (16GB+ VRAM recommended)

## License

[Add your license here]

## Support

For issues or questions:
- Check [docs/LLM_SETUP.md](docs/LLM_SETUP.md) for troubleshooting
- Review logs for error details
- Open an issue on GitHub