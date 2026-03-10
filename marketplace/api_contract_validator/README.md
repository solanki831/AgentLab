---
language:
- en
license: apache-2.0
tags:
- api
- contract
- schema
- validation
- testing
---

# AI API Contract Validator

Validates API responses against expected contracts and schemas. Detects breaking changes, missing fields, and type mismatches.

## Version
1.0.0

## Category
API Testing

## Capabilities
- JSON schema validation
- Response structure analysis
- Type checking
- Breaking change detection
- OpenAPI compatibility

## Requirements
- Python 3.8+
- httpx
- asyncio
- jsonschema

## Usage

```python
from framework.advanced_agents import api_contract_validator

# Run the agent
result = await api_contract_validator("https://your-url.com")
print(result)
```

## Publisher
AI Testing Suite

## Support
support@aitestingsuite.com

## License
Apache 2.0
