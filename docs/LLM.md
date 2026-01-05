# LLM Setup (Classifier + Summarizer)

FlightSense uses an LLM in two places:

- Classification (segment + label + priority + sentiment)
- Summarization (used for Jira descriptions and email summaries)

## 1) Classification

### What it does

The classifier turns a raw review into a small set of labeled segments stored in `processed_reviews`.

Key files:

- models/artifacts/label_map.json: label definitions and priority guidance
- models/artifacts/llm_config.json: default classifier model/provider settings
- packages/llm/prompts.py: strict JSON prompt and segmentation rules
- packages/llm/classifier.py: normalization, de-duplication, and validation of model output

### Configuration

The classifier reads defaults from models/artifacts/llm_config.json and allows environment overrides:

- LLM_PROVIDER: openai or vllm
- LLM_MODEL: model name
- OPENAI_API_KEY: required for OpenAI
- OPENAI_BASE_URL: optional (OpenAI-compatible endpoints)

Minimum required (OpenAI):

- OPENAI_API_KEY

Recommended for predictability:

- LLM_PROVIDER=openai
- LLM_MODEL=gpt-4o-mini

### Notes about output

- The classifier is configured to output strict JSON.
- It prefers fewer segments and avoids emitting multiple segments with the same label.
- HIGH priority is intended to be rare and requires explicit severity.

## 2) Summarization (agents)

Summaries are used by:

- JiraTicketAgent: generates an AI summary in the Jira issue description
- EmailSummaryAgent: generates daily/weekly summaries and urgent alert summaries

The summarizer reads its settings from models/artifacts/llm_config_agents.json.

Key files:

- models/artifacts/llm_config_agents.json
- packages/llm/summarizer.py
- packages/llm/prompts.py (summarization template + department examples)

If you want to change the model/provider for summaries, edit models/artifacts/llm_config_agents.json.

## Provider options

### OpenAI

- Set OPENAI_API_KEY in the environment.
- Optionally set OPENAI_BASE_URL for OpenAI-compatible services.

### vLLM

- Set LLM_PROVIDER=vllm
- Set LLM_MODEL to your local model name/path

Note: vLLM requires additional dependencies and a suitable runtime (typically a GPU setup).

## Quick verification

Run this inside the API container:

```bash
docker-compose exec app python -c "from packages.llm.classifier import FeedbackClassifier; print(FeedbackClassifier().label_review('Flight delayed 2 hours and staff gave no updates.'))"
```

If you see an error about missing API keys, ensure OPENAI_API_KEY is set for the container.
