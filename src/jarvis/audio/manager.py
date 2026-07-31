from typing import Any

import sounddevice as sd


class AudioManager:
    def __init__(self) -> None:
        self.channels = 1

        self.input_device = self._find_best_input()
        self.output_device = self._find_best_output()

        input_info = sd.query_devices(
            self.input_device,
            kind="input",
        )

        self.sample_rate = int(
            input_info["default_samplerate"]
        )

        sd.default.device = (
            self.input_device,
            self.output_device,
        )

    def devices(self) -> Any:
        return sd.query_devices()

    def hostapis(self) -> Any:
        return sd.query_hostapis()

    def _find_best_input(self) -> int:
        devices = self.devices()
        hostapis = self.hostapis()

        api_priorities = (
            "Windows WASAPI",
            "Windows DirectSound",
            "MME",
            "Windows WDM-KS",
        )

        preferred_names = (
            "rode",
            "microphone",
            "mic",
        )

        excluded_names = (
            "stereo mix",
            "line in",
            "sound mapper",
            "primary sound capture",
        )

        for api_name in api_priorities:
            for preferred_name in preferred_names:
                for index, device in enumerate(devices):
                    if int(device["max_input_channels"]) <= 0:
                        continue

                    device_name = str(device["name"]).lower()
                    host_name = str(
                        hostapis[device["hostapi"]]["name"]
                    )

                    if host_name != api_name:
                        continue

                    if any(
                        excluded in device_name
                        for excluded in excluded_names
                    ):
                        continue

                    if preferred_name in device_name:
                        return index

        for index, device in enumerate(devices):
            if int(device["max_input_channels"]) <= 0:
                continue

            device_name = str(device["name"]).lower()

            if any(
                excluded in device_name
                for excluded in excluded_names
            ):
                continue

            return index

        raise RuntimeError(
            "No usable microphone input device found."
        )

    def _find_best_output(self) -> int:
        devices = self.devices()
        hostapis = self.hostapis()

        api_priorities = (
            "Windows WASAPI",
            "Windows DirectSound",
            "MME",
            "Windows WDM-KS",
        )

        preferred_names = (
            "speakers",
            "headphones",
            "realtek",
        )

        excluded_names = (
            "digital output",
            "spdif",
            "display audio",
        )

        for api_name in api_priorities:
            for preferred_name in preferred_names:
                for index, device in enumerate(devices):
                    if int(device["max_output_channels"]) <= 0:
                        continue

                    device_name = str(device["name"]).lower()
                    host_name = str(
                        hostapis[device["hostapi"]]["name"]
                    )

                    if host_name != api_name:
                        continue

                    if any(
                        excluded in device_name
                        for excluded in excluded_names
                    ):
                        continue

                    if preferred_name in device_name:
                        return index

        for index, device in enumerate(devices):
            if int(device["max_output_channels"]) > 0:
                return index

        raise RuntimeError(
            "No usable output device found."
        )

    def print_devices(self) -> None:
        devices = self.devices()
        hostapis = self.hostapis()

        print("=" * 100)

        for index, device in enumerate(devices):
            host_name = hostapis[
                device["hostapi"]
            ]["name"]

            print(
                f"[{index}] {device['name']} | "
                f"API={host_name} | "
                f"IN={device['max_input_channels']} | "
                f"OUT={device['max_output_channels']} | "
                f"RATE={device['default_samplerate']}"
            )

        print("=" * 100)

        input_info = sd.query_devices(
            self.input_device,
            kind="input",
        )

        output_info = sd.query_devices(
            self.output_device,
            kind="output",
        )

        print(
            f"Selected Input : [{self.input_device}] "
            f"{input_info['name']}"
        )
        print(
            f"Selected Output: [{self.output_device}] "
            f"{output_info['name']}"
        )
        print(f"Sample Rate   : {self.sample_rate}")
        print(f"Channels      : {self.channels}")