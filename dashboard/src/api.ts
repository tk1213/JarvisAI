export type HealthStatus = 'healthy' | 'degraded'

export interface HealthResponse {
  status: HealthStatus
  checks: Record<string, boolean>
}

export interface SmartHomeDevice {
  id: string
  name: string
  room: string
  device_type: string
  online: boolean
  power: boolean
}

export interface SmartHomeDevicesResponse {
  connected: boolean
  devices: SmartHomeDevice[]
}

async function requestJson<T>(
  path: string,
  signal?: AbortSignal,
): Promise<T> {
  const response = await fetch(path, {
    method: 'GET',
    headers: {
      Accept: 'application/json',
    },
    signal,
  })

  if (!response.ok) {
    throw new Error(
      `Request failed with status ${response.status}`,
    )
  }

  return response.json() as Promise<T>
}

export function getHealth(
  signal?: AbortSignal,
): Promise<HealthResponse> {
  return requestJson<HealthResponse>(
    '/api/v1/health',
    signal,
  )
}

export function getSmartHomeDevices(
  signal?: AbortSignal,
): Promise<SmartHomeDevicesResponse> {
  return requestJson<SmartHomeDevicesResponse>(
    '/api/v1/smart-home/devices',
    signal,
  )
}