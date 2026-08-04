from __future__ import annotations

import asyncio
import hashlib
import hmac
import json
import time
from typing import Any
from urllib.parse import urlencode

import httpx

from jarvis.config import settings
from jarvis.smart_home.adapter import SmartHomeAdapter
from jarvis.smart_home.device import SmartDevice


class TuyaAdapter(SmartHomeAdapter):
    """
    Tuya Cloud API adapter.

    Supports:
    - Tuya Cloud authentication
    - Device discovery
    - Device status
    - Power-state mapping
    - Turn device on
    - Turn device off
    - Toggle device power
    """

    def __init__(self) -> None:
        self._access_id = (
            settings.tuya_access_id or ""
        ).strip()

        self._access_key = (
            settings.tuya_access_key or ""
        ).strip()

        self._endpoint = settings.tuya_endpoint.rstrip("/")

        self._access_token: str | None = None

        self._client = httpx.AsyncClient(
            base_url=self._endpoint,
            timeout=15.0,
        )

    @property
    def connected(self) -> bool:
        return self._access_token is not None

    async def connect(self) -> None:
        if self.connected:
            return

        self._validate_credentials()

        self._access_token = await self._request_token()

    async def disconnect(self) -> None:
        self._access_token = None

        if not self._client.is_closed:
            await self._client.aclose()

    async def list_devices(
        self,
    ) -> list[SmartDevice]:
        self._require_connection()

        response = await self._request(
            method="GET",
            path="/v2.0/cloud/thing/device",
            query={
                "page_size": "20",
            },
            access_token=self._access_token,
        )

        result = response.get("result")

        if not isinstance(result, list):
            raise TypeError(
                "Tuya device response result must be a list."
            )

        devices: list[SmartDevice] = []

        for item in result:
            if not isinstance(item, dict):
                continue

            device = await self._map_device(item)

            if device is not None:
                devices.append(device)

        return devices

    async def get_device(
        self,
        device_id: str,
    ) -> SmartDevice | None:
        self._require_connection()

        device_id = self._validate_device_id(
            device_id
        )

        devices = await self.list_devices()

        for device in devices:
            if device.id == device_id:
                return device

        return None

    async def get_status(
        self,
        device_id: str,
    ) -> list[dict[str, Any]]:
        self._require_connection()

        device_id = self._validate_device_id(
            device_id
        )

        response = await self._request(
            method="GET",
            path=(
                "/v1.0/iot-03/devices/"
                f"{device_id}/status"
            ),
            access_token=self._access_token,
        )

        result = response.get("result")

        if not isinstance(result, list):
            raise TypeError(
                "Tuya device status result must be a list."
            )

        return [
            item
            for item in result
            if isinstance(item, dict)
        ]

    async def turn_on(
        self,
        device_id: str,
    ) -> bool:
        return await self._set_power(
            device_id=device_id,
            power=True,
        )

    async def turn_off(
        self,
        device_id: str,
    ) -> bool:
        return await self._set_power(
            device_id=device_id,
            power=False,
        )

    async def toggle(
        self,
        device_id: str,
    ) -> bool:
        self._require_connection()

        device_id = self._validate_device_id(
            device_id
        )

        status = await self.get_status(
            device_id
        )

        current_power = self._extract_power_state(
            status
        )

        return await self._set_power(
            device_id=device_id,
            power=not current_power,
        )

    async def _set_power(
        self,
        *,
        device_id: str,
        power: bool,
    ) -> bool:
        self._require_connection()

        device_id = self._validate_device_id(
            device_id
        )

        switch_code = await self._find_power_code(
            device_id
        )

        await self._request(
            method="POST",
            path=(
                "/v1.0/iot-03/devices/"
                f"{device_id}/commands"
            ),
            body={
                "commands": [
                    {
                        "code": switch_code,
                        "value": power,
                    }
                ]
            },
            access_token=self._access_token,
        )

        max_attempts = 10
        retry_delay = 0.5

        for _ in range(max_attempts):
            await asyncio.sleep(
                retry_delay
            )

            status = await self.get_status(
                device_id
            )

            actual_power = self._extract_power_state(
                status
            )

            if actual_power is power:
                return True

        return False

    async def _find_power_code(
        self,
        device_id: str,
    ) -> str:
        status = await self.get_status(
            device_id
        )

        preferred_codes = (
            "switch",
            "switch_1",
        )

        for code in preferred_codes:
            for item in status:
                if item.get("code") == code:
                    return code

        raise LookupError(
            "No supported power switch datapoint "
            f"found for device '{device_id}'."
        )

    def _validate_credentials(self) -> None:
        if not self._access_id:
            raise ValueError(
                "TUYA_ACCESS_ID is required."
            )

        if not self._access_key:
            raise ValueError(
                "TUYA_ACCESS_KEY is required."
            )

        if not self._endpoint:
            raise ValueError(
                "TUYA_ENDPOINT is required."
            )

    def _require_connection(self) -> None:
        if not self.connected:
            raise RuntimeError(
                "TuyaAdapter is not connected."
            )

    @staticmethod
    def _validate_device_id(
        device_id: str,
    ) -> str:
        if not isinstance(
            device_id,
            str,
        ):
            raise TypeError(
                "device_id must be a string."
            )

        device_id = device_id.strip()

        if not device_id:
            raise ValueError(
                "device_id is required."
            )

        return device_id

    async def _request_token(self) -> str:
        response = await self._request(
            method="GET",
            path="/v1.0/token",
            query={
                "grant_type": "1",
            },
            access_token=None,
        )

        result = response.get("result")

        if not isinstance(result, dict):
            raise TypeError(
                "Tuya token response is missing result."
            )

        access_token = result.get(
            "access_token"
        )

        if not isinstance(
            access_token,
            str,
        ):
            raise TypeError(
                "Tuya token response is missing access_token."
            )

        access_token = access_token.strip()

        if not access_token:
            raise RuntimeError(
                "Tuya returned an empty access_token."
            )

        return access_token

    async def _map_device(
        self,
        data: dict[str, Any],
    ) -> SmartDevice | None:
        device_id = data.get("id")

        if not isinstance(
            device_id,
            str,
        ):
            return None

        device_id = device_id.strip()

        if not device_id:
            return None

        custom_name = data.get(
            "customName"
        )

        name = data.get(
            "name"
        )

        if (
            isinstance(custom_name, str)
            and custom_name.strip()
        ):
            device_name = custom_name.strip()

        elif (
            isinstance(name, str)
            and name.strip()
        ):
            device_name = name.strip()

        else:
            device_name = device_id

        category = data.get(
            "category"
        )

        if not isinstance(
            category,
            str,
        ):
            category = "unknown"

        online = data.get(
            "isOnline",
            False,
        )

        if not isinstance(
            online,
            bool,
        ):
            online = False

        status = await self.get_status(
            device_id
        )

        power = self._extract_power_state(
            status
        )

        return SmartDevice(
            id=device_id,
            name=device_name,
            room="",
            device_type=category,
            online=online,
            power=power,
        )

    @staticmethod
    def _extract_power_state(
        status: list[dict[str, Any]],
    ) -> bool:
        preferred_codes = (
            "switch",
            "switch_1",
        )

        for code in preferred_codes:
            for item in status:
                if item.get("code") != code:
                    continue

                value = item.get("value")

                if isinstance(
                    value,
                    bool,
                ):
                    return value

        return False

    async def _request(
        self,
        *,
        method: str,
        path: str,
        query: dict[str, str] | None = None,
        body: dict[str, Any] | None = None,
        access_token: str | None,
    ) -> dict[str, Any]:
        method = method.upper()

        query_string = ""

        if query:
            query_string = urlencode(
                sorted(query.items())
            )

        request_path = path

        if query_string:
            request_path = (
                f"{path}?{query_string}"
            )

        if body is None:
            body_bytes = b""

        else:
            body_text = json.dumps(
                body,
                separators=(",", ":"),
                ensure_ascii=False,
            )

            body_bytes = body_text.encode(
                "utf-8"
            )

        timestamp = str(
            int(time.time() * 1000)
        )

        body_hash = hashlib.sha256(
            body_bytes
        ).hexdigest()

        string_to_sign = (
            f"{method}\n"
            f"{body_hash}\n"
            "\n"
            f"{request_path}"
        )

        sign_payload = (
            self._access_id
            + (access_token or "")
            + timestamp
            + string_to_sign
        )

        signature = hmac.new(
            self._access_key.encode(
                "utf-8"
            ),
            sign_payload.encode(
                "utf-8"
            ),
            hashlib.sha256,
        ).hexdigest().upper()

        headers = {
            "client_id": self._access_id,
            "sign": signature,
            "sign_method": "HMAC-SHA256",
            "t": timestamp,
            "lang": "en",
        }

        if access_token:
            headers[
                "access_token"
            ] = access_token

        if body is not None:
            headers[
                "Content-Type"
            ] = "application/json"

        http_response = await self._client.request(
            method=method,
            url=request_path,
            headers=headers,
            content=(
                body_bytes
                if body is not None
                else None
            ),
        )

        http_response.raise_for_status()

        data = http_response.json()

        if not isinstance(
            data,
            dict,
        ):
            raise TypeError(
                "Tuya returned an invalid response."
            )

        success = data.get(
            "success",
            False,
        )

        if not success:
            code = data.get(
                "code"
            )
            message = data.get(
                "msg"
            )

            raise RuntimeError(
                "Tuya API request failed: "
                f"code={code}, "
                f"message={message}"
            )

        return data