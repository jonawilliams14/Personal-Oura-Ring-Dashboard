from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import date
from typing import Any

import requests

BASE_URL = "https://api.ouraring.com/v2/usercollection"


class OuraConfigurationError(RuntimeError):
    """Raised when the Oura client is missing required configuration."""


@dataclass(frozen=True)
class OuraClient:
    access_token: str
    base_url: str = BASE_URL

    @classmethod
    def from_env(cls) -> "OuraClient":
        token = os.environ.get("OURA_ACCESS_TOKEN")
        if not token or token == "your_personal_access_token_here":
            raise OuraConfigurationError(
                "Set OURA_ACCESS_TOKEN before fetching Oura data."
            )
        return cls(access_token=token)

    def fetch_collection(
        self,
        endpoint: str,
        start_date: date,
        end_date: date,
    ) -> list[dict[str, Any]]:
        records: list[dict[str, Any]] = []
        next_token: str | None = None

        while True:
            params: dict[str, str] = {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
            }
            if next_token:
                params["next_token"] = next_token

            response = requests.get(
                f"{self.base_url}/{endpoint}",
                headers={"Authorization": f"Bearer {self.access_token}"},
                params=params,
                timeout=30,
            )
            response.raise_for_status()

            payload = response.json()
            records.extend(payload.get("data", []))
            next_token = payload.get("next_token")
            if not next_token:
                return records
