from __future__ import annotations

import asyncio
import hashlib
import hmac
import json
from unittest.mock import AsyncMock, Mock, patch

import pytest

from jarvis.smart_home.device import SmartDevice
from jarvis.smart_home.tuya_adapter import TuyaAdapter


@pytest.fixture
def adapter() -> TuyaAdapter:
    instance = TuyaAdapter()

    instance._access_id = "test-access-id"
    instance._access_key = "test-access-key"
    instance._endpoint = "https://openapi-sg.iotbing.com"

    return instance


def test_tuya_adapter_starts_disconnected(
    adapter: TuyaAdapter,
) -> None:
    assert adapter.connected is False


def test_tuya_adapter_rejects_missing_access_id(
    adapter: TuyaAdapter,
) -> None:
    adapter._access_id = ""

    with pytest.raises(
        ValueError,
        match="TUYA_ACCESS_ID",
    ):
        adapter._validate_credentials()


def test_tuya_adapter_rejects_missing_access_key(
    adapter: TuyaAdapter,
) -> None:
    adapter._access_key = ""

    with pytest.raises(
        ValueError,
        match="TUYA_ACCESS_KEY",
    ):
        adapter._validate_credentials()


def test_tuya_adapter_rejects_empty_endpoint(
    adapter: TuyaAdapter,
) -> None:
    adapter._endpoint = ""

    with pytest.raises(
        ValueError,
        match="TUYA_ENDPOINT",
    ):
        adapter._validate_credentials()


@pytest.mark.asyncio
async def test_connect_requests_token_once(
    adapter: TuyaAdapter,
) -> None:
    adapter._request_token = AsyncMock(  # type: ignore[method-assign]
        return_value="test-token"
    )

    await adapter.connect()

    assert adapter.connected is True
    assert adapter._access_token == "test-token"

    adapter._request_token.assert_awaited_once()  # type: ignore[attr-defined]

    await adapter.connect()

    adapter._request_token.assert_awaited_once()  # type: ignore[attr-defined]

    await adapter.disconnect()


@pytest.mark.asyncio
async def test_disconnect_clears_access_token(
    adapter: TuyaAdapter,
) -> None:
    adapter._access_token = "test-token"

    await adapter.disconnect()

    assert adapter.connected is False


def test_validate_device_id_trims_whitespace() -> None:
    assert (
        TuyaAdapter._validate_device_id(
            "  device-123  "
        )
        == "device-123"
    )


@pytest.mark.parametrize(
    "device_id",
    [
        "",
        "   ",
    ],
)
def test_validate_device_id_rejects_empty_values(
    device_id: str,
) -> None:
    with pytest.raises(
        ValueError,
        match="device_id is required",
    ):
        TuyaAdapter._validate_device_id(
            device_id
        )


def test_validate_device_id_rejects_non_string() -> None:
    with pytest.raises(
        TypeError,
        match="device_id must be a string",
    ):
        TuyaAdapter._validate_device_id(  # type: ignore[arg-type]
            123
        )

@pytest.mark.asyncio
async def test_request_token_uses_expected_contract(
    adapter: TuyaAdapter,
) -> None:
    adapter._request = AsyncMock(  # type: ignore[method-assign]
        return_value={
            "result": {
                "access_token": "test-token",
            },
        }
    )

    token = await adapter._request_token()

    assert token == "test-token"

    adapter._request.assert_awaited_once_with(  # type: ignore[attr-defined]
        method="GET",
        path="/v1.0/token",
        query={
            "grant_type": "1",
        },
        access_token=None,
    )


@pytest.mark.asyncio
async def test_request_token_trims_token(
    adapter: TuyaAdapter,
) -> None:
    adapter._request = AsyncMock(  # type: ignore[method-assign]
        return_value={
            "result": {
                "access_token": "  test-token  ",
            },
        }
    )

    token = await adapter._request_token()

    assert token == "test-token"


@pytest.mark.asyncio
async def test_request_token_rejects_missing_result(
    adapter: TuyaAdapter,
) -> None:
    adapter._request = AsyncMock(  # type: ignore[method-assign]
        return_value={}
    )

    with pytest.raises(
        TypeError,
        match="missing result",
    ):
        await adapter._request_token()


@pytest.mark.asyncio
async def test_request_token_rejects_non_object_result(
    adapter: TuyaAdapter,
) -> None:
    adapter._request = AsyncMock(  # type: ignore[method-assign]
        return_value={
            "result": [],
        }
    )

    with pytest.raises(
        TypeError,
        match="missing result",
    ):
        await adapter._request_token()


@pytest.mark.asyncio
async def test_request_token_rejects_missing_access_token(
    adapter: TuyaAdapter,
) -> None:
    adapter._request = AsyncMock(  # type: ignore[method-assign]
        return_value={
            "result": {},
        }
    )

    with pytest.raises(
        TypeError,
        match="missing access_token",
    ):
        await adapter._request_token()


@pytest.mark.asyncio
async def test_request_token_rejects_non_string_access_token(
    adapter: TuyaAdapter,
) -> None:
    adapter._request = AsyncMock(  # type: ignore[method-assign]
        return_value={
            "result": {
                "access_token": 123,
            },
        }
    )

    with pytest.raises(
        TypeError,
        match="missing access_token",
    ):
        await adapter._request_token()


@pytest.mark.asyncio
async def test_request_token_rejects_empty_access_token(
    adapter: TuyaAdapter,
) -> None:
    adapter._request = AsyncMock(  # type: ignore[method-assign]
        return_value={
            "result": {
                "access_token": "   ",
            },
        }
    )

    with pytest.raises(
        RuntimeError,
        match="empty access_token",
    ):
        await adapter._request_token()

@pytest.mark.asyncio
async def test_request_builds_expected_get_signature(
    adapter: TuyaAdapter,
) -> None:
    response = Mock()
    response.raise_for_status = Mock()
    response.json = Mock(
        return_value={
            "success": True,
            "result": {},
        }
    )

    adapter._client.request = AsyncMock(
        return_value=response
    )

    timestamp = 1_700_000_000.123

    with patch(
        "jarvis.smart_home.tuya_adapter.time.time",
        return_value=timestamp,
    ):
        result = await adapter._request(
            method="get",
            path="/v1.0/token",
            query={
                "z": "9",
                "grant_type": "1",
                "a": "1",
            },
            access_token=None,
        )

    expected_timestamp = str(
        int(timestamp * 1000)
    )

    request_path = (
        "/v1.0/token?"
        "a=1&grant_type=1&z=9"
    )

    body_hash = hashlib.sha256(
        b""
    ).hexdigest()

    string_to_sign = (
        "GET\n"
        f"{body_hash}\n"
        "\n"
        f"{request_path}"
    )

    sign_payload = (
        "test-access-id"
        + expected_timestamp
        + string_to_sign
    )

    expected_signature = hmac.new(
        b"test-access-key",
        sign_payload.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest().upper()

    adapter._client.request.assert_awaited_once_with(
        method="GET",
        url=request_path,
        headers={
            "client_id": "test-access-id",
            "sign": expected_signature,
            "sign_method": "HMAC-SHA256",
            "t": expected_timestamp,
            "lang": "en",
        },
        content=None,
    )

    assert result == {
        "success": True,
        "result": {},
    }


@pytest.mark.asyncio
async def test_request_builds_expected_post_signature(
    adapter: TuyaAdapter,
) -> None:
    response = Mock()
    response.raise_for_status = Mock()
    response.json = Mock(
        return_value={
            "success": True,
            "result": True,
        }
    )

    adapter._client.request = AsyncMock(
        return_value=response
    )

    timestamp = 1_700_000_001.456

    body = {
        "commands": [
            {
                "code": "switch_1",
                "value": True,
            }
        ]
    }

    body_bytes = json.dumps(
        body,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")

    with patch(
        "jarvis.smart_home.tuya_adapter.time.time",
        return_value=timestamp,
    ):
        result = await adapter._request(
            method="post",
            path="/v1.0/iot-03/devices/device-1/commands",
            body=body,
            access_token="token-123",
        )

    expected_timestamp = str(
        int(timestamp * 1000)
    )

    body_hash = hashlib.sha256(
        body_bytes
    ).hexdigest()

    request_path = (
        "/v1.0/iot-03/devices/"
        "device-1/commands"
    )

    string_to_sign = (
        "POST\n"
        f"{body_hash}\n"
        "\n"
        f"{request_path}"
    )

    sign_payload = (
        "test-access-id"
        + "token-123"
        + expected_timestamp
        + string_to_sign
    )

    expected_signature = hmac.new(
        b"test-access-key",
        sign_payload.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest().upper()

    adapter._client.request.assert_awaited_once_with(
        method="POST",
        url=request_path,
        headers={
            "client_id": "test-access-id",
            "sign": expected_signature,
            "sign_method": "HMAC-SHA256",
            "t": expected_timestamp,
            "lang": "en",
            "access_token": "token-123",
            "Content-Type": "application/json",
        },
        content=body_bytes,
    )

    assert result["success"] is True


@pytest.mark.asyncio
async def test_request_propagates_http_error(
    adapter: TuyaAdapter,
) -> None:
    response = Mock()
    response.raise_for_status = Mock(
        side_effect=RuntimeError(
            "HTTP failure"
        )
    )

    adapter._client.request = AsyncMock(
        return_value=response
    )

    with pytest.raises(
        RuntimeError,
        match="HTTP failure",
    ):
        await adapter._request(
            method="GET",
            path="/test",
            access_token=None,
        )


@pytest.mark.asyncio
async def test_request_rejects_non_object_json(
    adapter: TuyaAdapter,
) -> None:
    response = Mock()
    response.raise_for_status = Mock()
    response.json = Mock(
        return_value=[]
    )

    adapter._client.request = AsyncMock(
        return_value=response
    )

    with pytest.raises(
        TypeError,
        match="invalid response",
    ):
        await adapter._request(
            method="GET",
            path="/test",
            access_token=None,
        )


@pytest.mark.asyncio
async def test_request_rejects_tuya_failure_response(
    adapter: TuyaAdapter,
) -> None:
    response = Mock()
    response.raise_for_status = Mock()
    response.json = Mock(
        return_value={
            "success": False,
            "code": 1010,
            "msg": "token invalid",
        }
    )

    adapter._client.request = AsyncMock(
        return_value=response
    )

    with pytest.raises(
        RuntimeError,
        match=(
            "code=1010, "
            "message=token invalid"
        ),
    ):
        await adapter._request(
            method="GET",
            path="/test",
            access_token="bad-token",
        )


@pytest.mark.asyncio
async def test_request_missing_success_is_failure(
    adapter: TuyaAdapter,
) -> None:
    response = Mock()
    response.raise_for_status = Mock()
    response.json = Mock(
        return_value={
            "result": {},
        }
    )

    adapter._client.request = AsyncMock(
        return_value=response
    )

    with pytest.raises(
        RuntimeError,
        match="Tuya API request failed",
    ):
        await adapter._request(
            method="GET",
            path="/test",
            access_token=None,
        )

@pytest.mark.asyncio
async def test_list_devices_maps_valid_devices(
    adapter: TuyaAdapter,
) -> None:
    adapter._access_token = "token-123"

    adapter._request = AsyncMock(  # type: ignore[method-assign]
        return_value={
            "success": True,
            "result": [
                {
                    "id": "device-1",
                    "name": "Living Room Light",
                    "category": "dj",
                    "isOnline": True,
                },
                {
                    "id": "device-2",
                    "customName": "Bedroom Lamp",
                    "name": "Original Name",
                    "category": "dj",
                    "isOnline": False,
                },
            ],
        }
    )

    async def fake_get_status(
        device_id: str,
    ) -> list[dict[str, object]]:
        if device_id == "device-1":
            return [
                {
                    "code": "switch_1",
                    "value": True,
                }
            ]

        return [
            {
                "code": "switch",
                "value": False,
            }
        ]

    adapter.get_status = AsyncMock(  # type: ignore[method-assign]
        side_effect=fake_get_status
    )

    devices = await adapter.list_devices()

    assert len(devices) == 2

    assert devices[0].id == "device-1"
    assert devices[0].name == "Living Room Light"
    assert devices[0].room == ""
    assert devices[0].device_type == "dj"
    assert devices[0].online is True
    assert devices[0].power is True

    assert devices[1].id == "device-2"
    assert devices[1].name == "Bedroom Lamp"
    assert devices[1].room == ""
    assert devices[1].device_type == "dj"
    assert devices[1].online is False
    assert devices[1].power is False

    adapter._request.assert_awaited_once_with(  # type: ignore[attr-defined]
        method="GET",
        path="/v2.0/cloud/thing/device",
        query={
            "page_size": "20",
        },
        access_token="token-123",
    )


@pytest.mark.asyncio
async def test_list_devices_skips_non_object_items(
    adapter: TuyaAdapter,
) -> None:
    adapter._access_token = "token-123"

    adapter._request = AsyncMock(  # type: ignore[method-assign]
        return_value={
            "success": True,
            "result": [
                None,
                "invalid",
                123,
                [],
                {
                    "id": "device-1",
                    "name": "Lamp",
                    "category": "dj",
                    "isOnline": True,
                },
            ],
        }
    )

    adapter.get_status = AsyncMock(  # type: ignore[method-assign]
        return_value=[]
    )

    devices = await adapter.list_devices()

    assert len(devices) == 1
    assert devices[0].id == "device-1"


@pytest.mark.asyncio
async def test_list_devices_skips_device_without_valid_id(
    adapter: TuyaAdapter,
) -> None:
    adapter._access_token = "token-123"

    adapter._request = AsyncMock(  # type: ignore[method-assign]
        return_value={
            "success": True,
            "result": [
                {},
                {
                    "id": "",
                    "name": "Empty ID",
                },
                {
                    "id": "   ",
                    "name": "Whitespace ID",
                },
                {
                    "id": 123,
                    "name": "Numeric ID",
                },
            ],
        }
    )

    adapter.get_status = AsyncMock()  # type: ignore[method-assign]

    devices = await adapter.list_devices()

    assert devices == []
    adapter.get_status.assert_not_awaited()


@pytest.mark.asyncio
async def test_list_devices_rejects_non_list_result(
    adapter: TuyaAdapter,
) -> None:
    adapter._access_token = "token-123"

    adapter._request = AsyncMock(  # type: ignore[method-assign]
        return_value={
            "success": True,
            "result": {},
        }
    )

    with pytest.raises(
        TypeError,
        match="result must be a list",
    ):
        await adapter.list_devices()


@pytest.mark.asyncio
async def test_map_device_prefers_custom_name(
    adapter: TuyaAdapter,
) -> None:
    adapter.get_status = AsyncMock(  # type: ignore[method-assign]
        return_value=[
            {
                "code": "switch",
                "value": True,
            }
        ]
    )

    device = await adapter._map_device(
        {
            "id": " device-1 ",
            "customName": "  Kitchen Light  ",
            "name": "Fallback Name",
            "category": "dj",
            "isOnline": True,
        }
    )

    assert device is not None
    assert device.id == "device-1"
    assert device.name == "Kitchen Light"
    assert device.device_type == "dj"
    assert device.online is True
    assert device.power is True


@pytest.mark.asyncio
async def test_map_device_falls_back_to_name(
    adapter: TuyaAdapter,
) -> None:
    adapter.get_status = AsyncMock(  # type: ignore[method-assign]
        return_value=[]
    )

    device = await adapter._map_device(
        {
            "id": "device-1",
            "customName": "   ",
            "name": "  Garage Door  ",
            "category": "ckmkzq",
            "isOnline": True,
        }
    )

    assert device is not None
    assert device.name == "Garage Door"


@pytest.mark.asyncio
async def test_map_device_falls_back_to_device_id(
    adapter: TuyaAdapter,
) -> None:
    adapter.get_status = AsyncMock(  # type: ignore[method-assign]
        return_value=[]
    )

    device = await adapter._map_device(
        {
            "id": "device-1",
            "category": "dj",
        }
    )

    assert device is not None
    assert device.name == "device-1"


@pytest.mark.asyncio
async def test_map_device_normalizes_invalid_metadata(
    adapter: TuyaAdapter,
) -> None:
    adapter.get_status = AsyncMock(  # type: ignore[method-assign]
        return_value=[]
    )

    device = await adapter._map_device(
        {
            "id": "device-1",
            "category": 123,
            "isOnline": "yes",
        }
    )

    assert device is not None
    assert device.device_type == "unknown"
    assert device.online is False
    assert device.power is False

@pytest.mark.asyncio
async def test_get_device_returns_matching_device(
    adapter: TuyaAdapter,
) -> None:
    adapter._access_token = "token-123"

    expected = SmartDevice(
        id="device-2",
        name="Bedroom Lamp",
        room="",
        device_type="dj",
        online=True,
        power=False,
    )

    adapter.list_devices = AsyncMock(  # type: ignore[method-assign]
        return_value=[
            SmartDevice(
                id="device-1",
                name="Living Room",
                room="",
                device_type="dj",
            ),
            expected,
        ]
    )

    result = await adapter.get_device(
        "  device-2  "
    )

    assert result is expected


@pytest.mark.asyncio
async def test_get_device_returns_none_when_missing(
    adapter: TuyaAdapter,
) -> None:
    adapter._access_token = "token-123"

    adapter.list_devices = AsyncMock(  # type: ignore[method-assign]
        return_value=[]
    )

    result = await adapter.get_device(
        "missing-device"
    )

    assert result is None


@pytest.mark.asyncio
async def test_get_device_requires_connection(
    adapter: TuyaAdapter,
) -> None:
    with pytest.raises(
        RuntimeError,
        match="not connected",
    ):
        await adapter.get_device(
            "device-1"
        )


@pytest.mark.asyncio
async def test_get_status_uses_expected_endpoint(
    adapter: TuyaAdapter,
) -> None:
    adapter._access_token = "token-123"

    adapter._request = AsyncMock(  # type: ignore[method-assign]
        return_value={
            "success": True,
            "result": [
                {
                    "code": "switch_1",
                    "value": True,
                },
                "invalid",
                123,
            ],
        }
    )

    status = await adapter.get_status(
        "  device-1  "
    )

    assert status == [
        {
            "code": "switch_1",
            "value": True,
        }
    ]

    adapter._request.assert_awaited_once_with(  # type: ignore[attr-defined]
        method="GET",
        path=(
            "/v1.0/iot-03/devices/"
            "device-1/status"
        ),
        access_token="token-123",
    )


@pytest.mark.asyncio
async def test_get_status_rejects_non_list_result(
    adapter: TuyaAdapter,
) -> None:
    adapter._access_token = "token-123"

    adapter._request = AsyncMock(  # type: ignore[method-assign]
        return_value={
            "success": True,
            "result": {},
        }
    )

    with pytest.raises(
        TypeError,
        match="status result must be a list",
    ):
        await adapter.get_status(
            "device-1"
        )


@pytest.mark.asyncio
async def test_get_status_requires_connection(
    adapter: TuyaAdapter,
) -> None:
    with pytest.raises(
        RuntimeError,
        match="not connected",
    ):
        await adapter.get_status(
            "device-1"
        )


def test_extract_power_state_prefers_switch(
    adapter: TuyaAdapter,
) -> None:
    assert (
        adapter._extract_power_state(
            [
                {
                    "code": "switch_1",
                    "value": False,
                },
                {
                    "code": "switch",
                    "value": True,
                },
            ]
        )
        is True
    )


def test_extract_power_state_uses_switch_1_fallback(
    adapter: TuyaAdapter,
) -> None:
    assert (
        adapter._extract_power_state(
            [
                {
                    "code": "switch_1",
                    "value": True,
                }
            ]
        )
        is True
    )


@pytest.mark.parametrize(
    "status",
    [
        [],
        [
            {
                "code": "brightness",
                "value": 100,
            }
        ],
        [
            {
                "code": "switch",
                "value": "true",
            }
        ],
    ],
)
def test_extract_power_state_defaults_false(
    adapter: TuyaAdapter,
    status: list[dict[str, object]],
) -> None:
    assert (
        adapter._extract_power_state(
            status
        )
        is False
    )

@pytest.mark.asyncio
async def test_find_power_code_prefers_switch(
    adapter: TuyaAdapter,
) -> None:
    adapter.get_status = AsyncMock(  # type: ignore[method-assign]
        return_value=[
            {
                "code": "switch_1",
                "value": False,
            },
            {
                "code": "switch",
                "value": True,
            },
        ]
    )

    result = await adapter._find_power_code(
        "device-1"
    )

    assert result == "switch"


@pytest.mark.asyncio
async def test_find_power_code_uses_switch_1_fallback(
    adapter: TuyaAdapter,
) -> None:
    adapter.get_status = AsyncMock(  # type: ignore[method-assign]
        return_value=[
            {
                "code": "brightness",
                "value": 500,
            },
            {
                "code": "switch_1",
                "value": False,
            },
        ]
    )

    result = await adapter._find_power_code(
        "device-1"
    )

    assert result == "switch_1"


@pytest.mark.asyncio
async def test_find_power_code_rejects_unsupported_device(
    adapter: TuyaAdapter,
) -> None:
    adapter.get_status = AsyncMock(  # type: ignore[method-assign]
        return_value=[
            {
                "code": "brightness",
                "value": 500,
            },
            {
                "code": "temp_current",
                "value": 250,
            },
        ]
    )

    with pytest.raises(
        LookupError,
        match="No supported power switch datapoint",
    ):
        await adapter._find_power_code(
            "device-1"
        )


@pytest.mark.asyncio
async def test_find_power_code_requests_status_for_device(
    adapter: TuyaAdapter,
) -> None:
    adapter.get_status = AsyncMock(  # type: ignore[method-assign]
        return_value=[
            {
                "code": "switch",
                "value": False,
            }
        ]
    )

    await adapter._find_power_code(
        "device-123"
    )

    adapter.get_status.assert_awaited_once_with(  # type: ignore[attr-defined]
        "device-123"
    )

@pytest.mark.asyncio
async def test_turn_on_delegates_to_set_power(
    adapter: TuyaAdapter,
) -> None:
    adapter._set_power = AsyncMock(  # type: ignore[method-assign]
        return_value=True
    )

    result = await adapter.turn_on(
        "device-1"
    )

    assert result is True

    adapter._set_power.assert_awaited_once_with(  # type: ignore[attr-defined]
        device_id="device-1",
        power=True,
    )


@pytest.mark.asyncio
async def test_turn_off_delegates_to_set_power(
    adapter: TuyaAdapter,
) -> None:
    adapter._set_power = AsyncMock(  # type: ignore[method-assign]
        return_value=True
    )

    result = await adapter.turn_off(
        "device-1"
    )

    assert result is True

    adapter._set_power.assert_awaited_once_with(  # type: ignore[attr-defined]
        device_id="device-1",
        power=False,
    )


@pytest.mark.asyncio
async def test_toggle_turns_off_when_currently_on(
    adapter: TuyaAdapter,
) -> None:
    adapter._access_token = "token-123"

    adapter.get_status = AsyncMock(  # type: ignore[method-assign]
        return_value=[
            {
                "code": "switch",
                "value": True,
            }
        ]
    )

    adapter._set_power = AsyncMock(  # type: ignore[method-assign]
        return_value=True
    )

    result = await adapter.toggle(
        "  device-1  "
    )

    assert result is True

    adapter.get_status.assert_awaited_once_with(  # type: ignore[attr-defined]
        "device-1"
    )

    adapter._set_power.assert_awaited_once_with(  # type: ignore[attr-defined]
        device_id="device-1",
        power=False,
    )


@pytest.mark.asyncio
async def test_toggle_turns_on_when_currently_off(
    adapter: TuyaAdapter,
) -> None:
    adapter._access_token = "token-123"

    adapter.get_status = AsyncMock(  # type: ignore[method-assign]
        return_value=[
            {
                "code": "switch_1",
                "value": False,
            }
        ]
    )

    adapter._set_power = AsyncMock(  # type: ignore[method-assign]
        return_value=True
    )

    result = await adapter.toggle(
        "device-1"
    )

    assert result is True

    adapter._set_power.assert_awaited_once_with(  # type: ignore[attr-defined]
        device_id="device-1",
        power=True,
    )


@pytest.mark.asyncio
async def test_toggle_requires_connection(
    adapter: TuyaAdapter,
) -> None:
    with pytest.raises(
        RuntimeError,
        match="not connected",
    ):
        await adapter.toggle(
            "device-1"
        )

@pytest.mark.asyncio
async def test_set_power_sends_expected_command() -> None:
    adapter = TuyaAdapter()
    adapter._access_token = "token"

    adapter._find_power_code = AsyncMock(
        return_value="switch_1"
    )
    adapter._request = AsyncMock(
        return_value={"success": True}
    )
    adapter.get_status = AsyncMock(
        return_value=[
            {
                "code": "switch_1",
                "value": True,
            }
        ]
    )

    with patch(
        "jarvis.smart_home.tuya_adapter.asyncio.sleep",
        new=AsyncMock(),
    ):
        result = await adapter._set_power(
            device_id="device-1",
            power=True,
        )

    assert result is True

    adapter._request.assert_awaited_once_with(
        method="POST",
        path="/v1.0/iot-03/devices/device-1/commands",
        body={
            "commands": [
                {
                    "code": "switch_1",
                    "value": True,
                }
            ]
        },
        access_token="token",
    )


@pytest.mark.asyncio
async def test_set_power_retries_until_state_matches() -> None:
    adapter = TuyaAdapter()
    adapter._access_token = "token"

    adapter._find_power_code = AsyncMock(
        return_value="switch"
    )
    adapter._request = AsyncMock(
        return_value={"success": True}
    )
    adapter.get_status = AsyncMock(
        side_effect=[
            [{"code": "switch", "value": False}],
            [{"code": "switch", "value": False}],
            [{"code": "switch", "value": True}],
        ]
    )

    with patch(
        "jarvis.smart_home.tuya_adapter.asyncio.sleep",
        new=AsyncMock(),
    ) as sleep:
        result = await adapter._set_power(
            device_id="device-1",
            power=True,
        )

    assert result is True
    assert adapter.get_status.await_count == 3
    assert sleep.await_count == 3


@pytest.mark.asyncio
async def test_set_power_returns_false_after_retry_exhaustion() -> None:
    adapter = TuyaAdapter()
    adapter._access_token = "token"

    adapter._find_power_code = AsyncMock(
        return_value="switch"
    )
    adapter._request = AsyncMock(
        return_value={"success": True}
    )
    adapter.get_status = AsyncMock(
        return_value=[
            {
                "code": "switch",
                "value": False,
            }
        ]
    )

    with patch(
        "jarvis.smart_home.tuya_adapter.asyncio.sleep",
        new=AsyncMock(),
    ) as sleep:
        result = await adapter._set_power(
            device_id="device-1",
            power=True,
        )

    assert result is False
    assert adapter.get_status.await_count == 10
    assert sleep.await_count == 10


@pytest.mark.asyncio
async def test_set_power_requires_connection() -> None:
    adapter = TuyaAdapter()
    adapter._access_token = None

    with pytest.raises(
        RuntimeError,
        match="TuyaAdapter is not connected",
    ):
        await adapter._set_power(
            device_id="device-1",
            power=True,
        )


@pytest.mark.asyncio
async def test_set_power_does_not_verify_when_command_fails() -> None:
    adapter = TuyaAdapter()
    adapter._access_token = "token"

    adapter._find_power_code = AsyncMock(
        return_value="switch"
    )
    adapter._request = AsyncMock(
        side_effect=RuntimeError(
            "command failed"
        )
    )
    adapter.get_status = AsyncMock()

    with pytest.raises(
        RuntimeError,
        match="command failed",
    ):
        await adapter._set_power(
            device_id="device-1",
            power=True,
        )

    adapter.get_status.assert_not_awaited()

@pytest.mark.asyncio
async def test_set_power_verifies_turn_off_success(
    adapter: TuyaAdapter,
) -> None:
    adapter._access_token = "token"

    adapter._find_power_code = AsyncMock(
        return_value="switch"
    )
    adapter._request = AsyncMock(
        return_value={"success": True}
    )
    adapter.get_status = AsyncMock(
        return_value=[
            {
                "code": "switch",
                "value": False,
            }
        ]
    )

    with patch(
        "jarvis.smart_home.tuya_adapter.asyncio.sleep",
        new=AsyncMock(),
    ):
        result = await adapter._set_power(
            device_id="device-1",
            power=False,
        )

    assert result is True


@pytest.mark.asyncio
async def test_set_power_does_not_accept_missing_switch_state(
    adapter: TuyaAdapter,
) -> None:
    adapter._access_token = "token"

    adapter._find_power_code = AsyncMock(
        return_value="switch"
    )
    adapter._request = AsyncMock(
        return_value={"success": True}
    )
    adapter.get_status = AsyncMock(
        return_value=[
            {
                "code": "brightness",
                "value": 500,
            }
        ]
    )

    with patch(
        "jarvis.smart_home.tuya_adapter.asyncio.sleep",
        new=AsyncMock(),
    ):
        result = await adapter._set_power(
            device_id="device-1",
            power=True,
        )

    assert result is False
    assert adapter.get_status.await_count == 10


@pytest.mark.asyncio
async def test_set_power_does_not_accept_non_boolean_switch_state(
    adapter: TuyaAdapter,
) -> None:
    adapter._access_token = "token"

    adapter._find_power_code = AsyncMock(
        return_value="switch"
    )
    adapter._request = AsyncMock(
        return_value={"success": True}
    )
    adapter.get_status = AsyncMock(
        return_value=[
            {
                "code": "switch",
                "value": "true",
            }
        ]
    )

    with patch(
        "jarvis.smart_home.tuya_adapter.asyncio.sleep",
        new=AsyncMock(),
    ):
        result = await adapter._set_power(
            device_id="device-1",
            power=True,
        )

    assert result is False
    assert adapter.get_status.await_count == 10


@pytest.mark.asyncio
async def test_set_power_stops_immediately_after_match(
    adapter: TuyaAdapter,
) -> None:
    adapter._access_token = "token"

    adapter._find_power_code = AsyncMock(
        return_value="switch"
    )
    adapter._request = AsyncMock(
        return_value={"success": True}
    )
    adapter.get_status = AsyncMock(
        side_effect=[
            [{"code": "switch", "value": False}],
            [{"code": "switch", "value": True}],
            [{"code": "switch", "value": False}],
        ]
    )

    with patch(
        "jarvis.smart_home.tuya_adapter.asyncio.sleep",
        new=AsyncMock(),
    ) as sleep:
        result = await adapter._set_power(
            device_id="device-1",
            power=True,
        )

    assert result is True
    assert adapter.get_status.await_count == 2
    assert sleep.await_count == 2

@pytest.mark.asyncio
async def test_request_propagates_network_error(
    adapter: TuyaAdapter,
) -> None:
    adapter._client.request = AsyncMock(
        side_effect=OSError(
            "network unavailable"
        )
    )

    with pytest.raises(
        OSError,
        match="network unavailable",
    ):
        await adapter._request(
            method="GET",
            path="/test",
            access_token=None,
        )


@pytest.mark.asyncio
async def test_request_propagates_json_decode_error(
    adapter: TuyaAdapter,
) -> None:
    response = Mock()
    response.raise_for_status = Mock()
    response.json = Mock(
        side_effect=ValueError(
            "invalid json"
        )
    )

    adapter._client.request = AsyncMock(
        return_value=response
    )

    with pytest.raises(
        ValueError,
        match="invalid json",
    ):
        await adapter._request(
            method="GET",
            path="/test",
            access_token=None,
        )


@pytest.mark.asyncio
async def test_request_propagates_cancellation(
    adapter: TuyaAdapter,
) -> None:
    adapter._client.request = AsyncMock(
        side_effect=asyncio.CancelledError()
    )

    with pytest.raises(
        asyncio.CancelledError
    ):
        await adapter._request(
            method="GET",
            path="/test",
            access_token=None,
        )


@pytest.mark.asyncio
async def test_set_power_propagates_status_failure_during_verification(
    adapter: TuyaAdapter,
) -> None:
    adapter._access_token = "token"

    adapter._find_power_code = AsyncMock(
        return_value="switch"
    )

    adapter._request = AsyncMock(
        return_value={
            "success": True,
        }
    )

    adapter.get_status = AsyncMock(
        side_effect=RuntimeError(
            "status unavailable"
        )
    )

    with (
        patch(
            "jarvis.smart_home.tuya_adapter.asyncio.sleep",
            new=AsyncMock(),
        ),
        pytest.raises(
            RuntimeError,
            match="status unavailable",
        ),
    ):
        await adapter._set_power(
            device_id="device-1",
            power=True,
        )

    assert adapter.get_status.await_count == 1


@pytest.mark.asyncio
async def test_set_power_does_not_send_command_for_unsupported_device(
    adapter: TuyaAdapter,
) -> None:
    adapter._access_token = "token"

    adapter._find_power_code = AsyncMock(
        side_effect=LookupError(
            "No supported power switch datapoint"
        )
    )

    adapter._request = AsyncMock()

    with pytest.raises(
        LookupError,
        match="No supported power switch datapoint",
    ):
        await adapter._set_power(
            device_id="device-1",
            power=True,
        )

    adapter._request.assert_not_awaited()

@pytest.mark.asyncio
async def test_connect_sets_token_on_success(
    adapter: TuyaAdapter,
) -> None:
    adapter._request_token = AsyncMock(
        return_value="token-123"
    )

    await adapter.connect()

    assert adapter.connected is True
    assert adapter._access_token == "token-123"


@pytest.mark.asyncio
async def test_connect_does_not_request_new_token_when_already_connected(
    adapter: TuyaAdapter,
) -> None:
    adapter._access_token = "existing-token"
    adapter._request_token = AsyncMock()

    await adapter.connect()

    adapter._request_token.assert_not_awaited()
    assert adapter._access_token == "existing-token"


@pytest.mark.asyncio
async def test_connect_does_not_set_token_when_token_request_fails(
    adapter: TuyaAdapter,
) -> None:
    adapter._request_token = AsyncMock(
        side_effect=RuntimeError(
            "token unavailable"
        )
    )

    with pytest.raises(
        RuntimeError,
        match="token unavailable",
    ):
        await adapter.connect()

    assert adapter.connected is False
    assert adapter._access_token is None


@pytest.mark.asyncio
async def test_connect_propagates_cancellation(
    adapter: TuyaAdapter,
) -> None:
    adapter._request_token = AsyncMock(
        side_effect=asyncio.CancelledError()
    )

    with pytest.raises(
        asyncio.CancelledError
    ):
        await adapter.connect()

    assert adapter.connected is False
    assert adapter._access_token is None


@pytest.mark.asyncio
async def test_disconnect_clears_token_and_closes_client(
    adapter: TuyaAdapter,
) -> None:
    adapter._access_token = "token-123"
    adapter._client.aclose = AsyncMock()

    await adapter.disconnect()

    assert adapter.connected is False
    assert adapter._access_token is None
    adapter._client.aclose.assert_awaited_once()


@pytest.mark.asyncio
async def test_disconnect_does_not_close_already_closed_client(
    adapter: TuyaAdapter,
) -> None:
    adapter._access_token = "token-123"

    client = Mock()
    client.is_closed = True
    client.aclose = AsyncMock()

    adapter._client = client  # type: ignore[assignment]

    await adapter.disconnect()

    assert adapter.connected is False
    client.aclose.assert_not_awaited()


@pytest.mark.asyncio
async def test_set_power_propagates_cancellation_during_verification_sleep(
    adapter: TuyaAdapter,
) -> None:
    adapter._access_token = "token"

    adapter._find_power_code = AsyncMock(
        return_value="switch"
    )
    adapter._request = AsyncMock(
        return_value={"success": True}
    )
    adapter.get_status = AsyncMock()

    with (
        patch(
            "jarvis.smart_home.tuya_adapter.asyncio.sleep",
            new=AsyncMock(
                side_effect=asyncio.CancelledError()
            ),
        ),
        pytest.raises(
            asyncio.CancelledError
        ),
    ):
        await adapter._set_power(
            device_id="device-1",
            power=True,
        )

    adapter.get_status.assert_not_awaited()


@pytest.mark.asyncio
async def test_set_power_propagates_cancellation_during_status_check(
    adapter: TuyaAdapter,
) -> None:
    adapter._access_token = "token"

    adapter._find_power_code = AsyncMock(
        return_value="switch"
    )
    adapter._request = AsyncMock(
        return_value={"success": True}
    )
    adapter.get_status = AsyncMock(
        side_effect=asyncio.CancelledError()
    )

    with (
        patch(
            "jarvis.smart_home.tuya_adapter.asyncio.sleep",
            new=AsyncMock(),
        ),
        pytest.raises(
            asyncio.CancelledError
        ),
    ):
        await adapter._set_power(
            device_id="device-1",
            power=True,
        )