import sounddevice as sd

device_id = 12
device = sd.query_devices(device_id)

print(device)

sd.check_input_settings(
    device=device_id,
    samplerate=16000,
    channels=1,
)

print("Microphone is ready.")