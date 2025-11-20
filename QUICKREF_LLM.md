# FlightSense LLM Integration - Quick Reference

## Installation

```bash
# Install OpenAI (recommended)
pip install openai

# Or install vLLM (for local inference, requires GPU)
pip install vllm
```

## Configuration

```bash
# Set environment variables
export OPENAI_API_KEY=sk-your-key-here
export LLM_PROVIDER=openai
export LLM_MODEL=gpt-4o-mini
```

## Quick Test

```bash
# Test your setup
python test_llm_setup.py
```

## Usage Examples

### Basic Client

```python
from packages.llm.client import LLMClient

client = LLMClient()
response = client.complete("Your prompt here")
```

### Labeling

```python
from packages.llm.classifier import FeedbackClassifier

classifier = FeedbackClassifier()
segments = classifier.label_review("Flight delayed. Baggage lost.")
# Returns: {"segments": [{"start": 0, "length": 15, "label": "flight_delay_cancellation"}, ...]}
```

### Classification

```python
from packages.llm.classifier import FeedbackClassifier

classifier = FeedbackClassifier()
df = classifier.classify_batch([
    "Great service!",
    "Terrible delays"
])
# Returns DataFrame with labels and sentiment
```

## Providers

| Provider | Setup | Cost | Speed | Privacy |
|----------|-------|------|-------|---------|
| OpenAI | Easy | Pay/use | Fast | External |
| vLLM | Hard | Free | Faster | Local |

## Common Issues

| Error | Solution |
|-------|----------|
| Import openai not found | `pip install openai` |
| API key required | `export OPENAI_API_KEY=sk-...` |
| Rate limit exceeded | Wait or upgrade OpenAI plan |
| Out of memory (vLLM) | Use smaller model |

## Environment Variables

```bash
# Required
OPENAI_API_KEY=sk-...           # Your OpenAI API key
LLM_PROVIDER=openai             # or "vllm"
LLM_MODEL=gpt-4o-mini           # Model name

# Optional
OPENAI_BASE_URL=...             # Custom API endpoint
JWT_SECRET_KEY=...              # For auth
JIRA_BASE_URL=...               # For tickets
JIRA_EMAIL=...
JIRA_API_TOKEN=...
```

## Model Recommendations

### OpenAI
- **gpt-4o-mini** - Fast, cheap, good quality (recommended)
- **gpt-4o** - Best quality, higher cost
- **gpt-3.5-turbo** - Legacy, cheapest

### vLLM
- **meta-llama/Llama-3.1-8B-Instruct** - Good balance
- **mistralai/Mistral-7B-Instruct-v0.2** - Fast
- **google/gemma-7b-it** - High quality

## Costs (OpenAI gpt-4o-mini)

- Input: ~$0.15 per 1M tokens
- Output: ~$0.60 per 1M tokens
- Typical feedback: ~200 tokens
- 1000 reviews: ~$0.15

## File Locations

```
packages/llm/
├── client.py              # Main LLM client
├── classifier.py          # Feedback classifier & labeling
├── prompts.py            # Prompt templates
└── README.md             # Detailed docs

docs/
├── LLM_SETUP.md          # Setup guide
└── IMPLEMENTATION_SUMMARY.md

test_llm_setup.py         # Test suite
examples_llm.py           # Usage examples
.env.example              # Config template
```

## Support

- Detailed guide: `docs/LLM_SETUP.md`
- API docs: `packages/llm/README.md`
- Test: `python test_llm_setup.py`
- Examples: `python examples_llm.py`
