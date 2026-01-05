# Deprecated

LLM documentation was consolidated.

Use:

- docs/LLM.md

# Test with a simple prompt
response = client.complete("Say hello!")
print(response)
```

## Usage in FlightSense

### Labeling Service

Automatically labels airline feedback with fine-grained categories:

```python
from packages.llm.classifier import FeedbackClassifier

classifier = FeedbackClassifier()

review = """
The flight was delayed by 3 hours with no explanation. 
When we finally boarded, the food was cold and the entertainment 
system wasn't working. My baggage also arrived damaged.
"""

# Label the review
result = classifier.label_review(review, max_segments=5)

print(result)
# Output:
# {
#   "segments": [
#     {"start": 0, "length": 54, "label": "flight_delay_cancellation"},
#     {"start": 89, "length": 21, "label": "inflight_experience_food_beverage"},
#     {"start": 115, "length": 45, "label": "inflight_experience_entertainment"},
#     {"start": 162, "length": 34, "label": "baggage_damaged"}
#   ]
# }
```


## Provider Options

### Option 1: OpenAI 

**Setup:**
```bash
pip install openai
export OPENAI_API_KEY=sk-...
export LLM_PROVIDER=openai
export LLM_MODEL=gpt-4o-mini
```

**Cost:** ~$0.15 per 1M input tokens, ~$0.60 per 1M output tokens (gpt-4o-mini)

### Option 2: vLLM (For Production/High Volume)

**Pros:**
- No per-request costs
- Fast inference with GPU
- Full data privacy
- Can use open-source models

**Cons:**
- Requires GPU (8GB+ VRAM)
- Complex setup
- Need to manage models
- Requires technical expertise

**Setup:**
```bash
pip install vllm
export LLM_PROVIDER=vllm
export LLM_MODEL=meta-llama/Llama-3.1-8B-Instruct
```


### Custom OpenAI-Compatible APIs

FlightSense supports any OpenAI-compatible API (Azure OpenAI, LocalAI, etc.):

```python
from packages.llm.client import LLMClient

client = LLMClient(
    provider="openai",
    base_url="https://your-custom-endpoint.com/v1",
    api_key="your-key",
    model="your-model"
)
```

### Programmatic Configuration

Override environment variables programmatically:

```python
# OpenAI
client = LLMClient(
    provider="openai",
    model="gpt-4o",
    api_key="sk-...",
    temperature=0.0,
    max_tokens=2048
)

# vLLM
client = LLMClient(
    provider="vllm",
    model="meta-llama/Llama-3.1-8B-Instruct",
    temperature=0.0,
    max_tokens=2048
)
```

### Error Handling

```python
from packages.llm.client import LLMClient

try:
    client = LLMClient()
    response = client.complete("Your prompt here")
except ImportError as e:
    print(f"Missing dependency: {e}")
    print("Install with: pip install openai")
except ValueError as e:
    print(f"Configuration error: {e}")
    print("Check your .env file and API keys")
except Exception as e:
    print(f"LLM error: {e}")
```

## Troubleshooting

### "Import openai could not be resolved"

**Solution:** Install the OpenAI package
```bash
pip install openai
```
### "Out of memory" (vLLM)

**Solution:** Use a smaller model or increase GPU memory:
```bash
export LLM_MODEL=meta-llama/Llama-3.1-8B-Instruct  # Instead of 70B
```

### JSON Parsing Errors

The LLM sometimes returns invalid JSON. The classifier has fallback handling:
```python
# In classifier.py - already implemented
try:
    data = json.loads(raw)
except json.JSONDecodeError:
    logger.error("LLM returned invalid JSON")
    # Returns default neutral classification
```
