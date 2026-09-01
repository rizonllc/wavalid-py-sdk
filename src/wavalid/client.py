from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Literal, Optional, TypedDict

NumberStatus = Literal["valid", "invalid", "limit"]


class ValidateResult(TypedDict):
    phoneNumber: str
    status: NumberStatus
    creditsRemaining: int


class BulkResultItem(TypedDict):
    phoneNumber: str
    status: Literal["valid", "invalid"]


class ValidateBulkResult(TypedDict):
    results: list[BulkResultItem]
    creditsUsed: int
    creditsRemaining: int


@dataclass
class ApiError(Exception):
    status_code: int
    message: str
    code: Optional[str] = None

    def __str__(self) -> str:
        return f"wavalid: {self.message} (status {self.status_code})"


class WavalidClient:
    """Client for the wavalid WhatsApp number validation API.

    baseUrl is the root domain only (e.g. "https://wavalid.com") — do not
    append "/api" or "/api/v1", the client adds that path itself.
    """

    def __init__(self, api_key: str, base_url: str) -> None:
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")

    def validate(
        self, phone_number: str, batch_id: Optional[int] = None
    ) -> ValidateResult:
        """Checks a single phone number and deducts one credit if the check completes."""
        body = {"phoneNumber": phone_number}
        if batch_id is not None:
            body["batchId"] = batch_id
        return self._request("/v1/validate", body)

    def validate_bulk(
        self, phone_numbers: list[str], batch_id: Optional[int] = None
    ) -> ValidateBulkResult:
        """Checks up to 100 numbers in one request, one credit per number checked."""
        body: dict = {"phoneNumbers": phone_numbers}
        if batch_id is not None:
            body["batchId"] = batch_id
        return self._request("/v1/validate/bulk", body)

    def _request(self, path: str, body: dict) -> dict:
        payload = json.dumps(body).encode("utf-8")
        request = urllib.request.Request(
            f"{self._base_url}/api{path}",
            data=payload,
            method="POST",
            headers={
                "Content-Type": "application/json",
                "x-api-key": self._api_key,
            },
        )

        try:
            with urllib.request.urlopen(request) as response:
                return json.loads(response.read())
        except urllib.error.HTTPError as error:
            data = json.loads(error.read() or b"{}")
            raise ApiError(
                status_code=data.get("statusCode", error.code),
                message=data.get("message", "Something went wrong"),
                code=data.get("code"),
            ) from None
