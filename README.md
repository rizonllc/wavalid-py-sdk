# wavalid-py-sdk

Python SDK for the [wavalid](https://wavalid.com) WhatsApp number validation API. wavalid checks whether a phone number is registered and active on WhatsApp; it does not send messages and does not store phone numbers.

## Install

```bash
pip install wavalid-py-sdk
```

Requires Python 3.9+. No dependencies — uses the standard library `urllib`.

## Authentication

Every request needs an API key, created from the wavalid dashboard. Never hardcode it — read it from an environment variable.

```python
import os
from wavalid import WavalidClient

client = WavalidClient(api_key=os.environ["WAVALID_API_KEY"], base_url="https://wavalid.com")
```

`base_url` is the root domain only — do not append `/api` or `/api/v1`, the client adds that path itself.

## `client.validate(phone_number, batch_id=None)`

Validates a single phone number.

```python
result = client.validate("+14155551234")
# result["status"]: "valid" | "invalid" | "limit"
```

## `client.validate_bulk(phone_numbers, batch_id=None)`

Validates up to 100 phone numbers in one request.

```python
bulk = client.validate_bulk(["+14155551234", "+447911123456"])
# bulk["results"], bulk["creditsUsed"], bulk["creditsRemaining"]
```

For more than 100 numbers, split the list into chunks of 100 and call `validate_bulk` once per chunk.

## Errors

Both methods raise `wavalid.ApiError` on any non-2xx response — always wrap calls in `try`/`except`, never assume success.

```python
from wavalid import ApiError

try:
    result = client.validate("+14155551234")
except ApiError as error:
    if error.code == "rateLimitExceeded":
        ...  # back off and retry later
    print(error.status_code, error.code, error.message)
```

| status_code | code                  | meaning                                                                                  |
| ----------- | --------------------- | ---------------------------------------------------------------------------------------- |
| 400         | (none)                | `phone_number` is not a valid international number, or `phone_numbers` is empty/over 100 |
| 401         | (none)                | missing or invalid API key                                                               |
| 402         | `insufficientCredits` | account has no credits left                                                              |
| 404         | (none)                | `batch_id` does not exist for this account                                               |
| 429         | `rateLimitExceeded`   | too many requests; back off                                                              |
| 502         | (none)                | upstream WhatsApp check failed; safe to retry                                            |

## Links

- API reference: https://wavalid.com/product/api
- Source / issues: https://github.com/rizonllc/wavalid-py-sdk
- License: MIT
