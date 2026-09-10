import {
  useCallback,
  useEffect,
  useState,
} from 'react'
import {
  getHealth,
  getSmartHomeDevices,
  type HealthResponse,
  type SmartHomeDevicesResponse,
} from './api'
import './App.css'

const REFRESH_INTERVAL_MS = 15_000

function formatCheckName(name: string): string {
  return name
    .split('_')
    .map(
      (word) =>
        word.charAt(0).toUpperCase() + word.slice(1),
    )
    .join(' ')
}

function formatRequestError(
  source: string,
  reason: unknown,
): string {
  const message =
    reason instanceof Error
      ? reason.message
      : 'เกิดข้อผิดพลาดที่ไม่ทราบสาเหตุ'

  return `${source}: ${message}`
}

function App() {
  const [health, setHealth] =
    useState<HealthResponse | null>(null)
  const [smartHome, setSmartHome] =
    useState<SmartHomeDevicesResponse | null>(null)
  const [errors, setErrors] = useState<string[]>([])
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [updatedAt, setUpdatedAt] =
    useState<Date | null>(null)

  const loadDashboard = useCallback(
    async (
      signal?: AbortSignal,
      showRefreshing = false,
    ) => {
      if (showRefreshing) {
        setRefreshing(true)
      }

      try {
        const [healthResult, smartHomeResult] =
          await Promise.allSettled([
            getHealth(signal),
            getSmartHomeDevices(signal),
          ])

        if (signal?.aborted) {
          return
        }

        const nextErrors: string[] = []
        let updated = false

        if (healthResult.status === 'fulfilled') {
          setHealth(healthResult.value)
          updated = true
        } else {
          nextErrors.push(
            formatRequestError(
              'System Health',
              healthResult.reason,
            ),
          )
        }

        if (smartHomeResult.status === 'fulfilled') {
          setSmartHome(smartHomeResult.value)
          updated = true
        } else {
          nextErrors.push(
            formatRequestError(
              'Smart Home',
              smartHomeResult.reason,
            ),
          )
        }

        if (updated) {
          setUpdatedAt(new Date())
        }

        setErrors(nextErrors)
      } finally {
        setLoading(false)
        setRefreshing(false)
      }
    },
    [],
  )

  useEffect(() => {
    const controller = new AbortController()

    const initialLoadId = window.setTimeout(() => {
      void loadDashboard(controller.signal)
    }, 0)

    const intervalId = window.setInterval(() => {
      void loadDashboard()
    }, REFRESH_INTERVAL_MS)

    return () => {
      controller.abort()
      window.clearTimeout(initialLoadId)
      window.clearInterval(intervalId)
    }
  }, [loadDashboard])

  const healthyChecks = health
    ? Object.values(health.checks).filter(Boolean).length
    : 0
  const totalChecks = health
    ? Object.keys(health.checks).length
    : 0
  const onlineDevices =
    smartHome?.devices.filter(
      (device) => device.online,
    ).length ?? 0
  const poweredDevices =
    smartHome?.devices.filter(
      (device) => device.power,
    ).length ?? 0

  return (
    <main className="dashboard-shell">
      <header className="dashboard-header">
        <div>
          <p className="eyebrow">
            JARVIS CONTROL CENTER
          </p>
          <h1>System overview</h1>
          <p className="header-description">
            สถานะระบบและอุปกรณ์ Smart Home แบบอ่านอย่างเดียว
          </p>
        </div>

        <div className="header-actions">
          <div
            className="updated-time"
            aria-live="polite"
          >
            <span>อัปเดตล่าสุด</span>
            <strong>
              {updatedAt
                ? updatedAt.toLocaleTimeString('th-TH', {
                    hour: '2-digit',
                    minute: '2-digit',
                    second: '2-digit',
                  })
                : '—'}
            </strong>
          </div>

          <button
            type="button"
            className="refresh-button"
            disabled={loading || refreshing}
            onClick={() =>
              void loadDashboard(undefined, true)
            }
          >
            {refreshing
              ? 'กำลังอัปเดต…'
              : 'อัปเดตข้อมูล'}
          </button>
        </div>
      </header>

      {errors.length > 0 && (
        <section
          className="error-banner"
          role="alert"
        >
          <div>
            <strong>
              ข้อมูลบางส่วนอัปเดตไม่สำเร็จ
            </strong>

            {errors.map((errorMessage) => (
              <p key={errorMessage}>
                {errorMessage}
              </p>
            ))}
          </div>

          <button
            type="button"
            onClick={() =>
              void loadDashboard(undefined, true)
            }
          >
            ลองอีกครั้ง
          </button>
        </section>
      )}

      {loading ? (
        <section
          className="loading-panel"
          aria-live="polite"
        >
          <div className="loading-orbit" />
          <p>กำลังตรวจสอบระบบ JarvisAI…</p>
        </section>
      ) : (
        <>
          <section
            className="summary-grid"
            aria-label="สรุปสถานะ"
          >
            <article className="summary-card primary-card">
              <span className="summary-label">
                SYSTEM HEALTH
              </span>
              <strong>
                {health
                  ? health.status === 'healthy'
                    ? 'Healthy'
                    : 'Degraded'
                  : 'Unknown'}
              </strong>
              <p>
                {health
                  ? `${healthyChecks} จาก ${totalChecks} ระบบย่อยพร้อมทำงาน`
                  : 'ยังไม่มีข้อมูลสถานะระบบ'}
              </p>
            </article>

            <article className="summary-card">
              <span className="summary-label">
                SMART HOME
              </span>
              <strong>
                {smartHome
                  ? smartHome.connected
                    ? 'Connected'
                    : 'Disconnected'
                  : 'Unknown'}
              </strong>
              <p>
                {smartHome
                  ? 'เชื่อมต่อผู้ให้บริการอุปกรณ์'
                  : 'ยังไม่มีข้อมูลการเชื่อมต่อ'}
              </p>
            </article>

            <article className="summary-card">
              <span className="summary-label">
                ONLINE DEVICES
              </span>
              <strong>
                {smartHome ? onlineDevices : '—'}
              </strong>
              <p>
                {smartHome
                  ? `จาก ${smartHome.devices.length} อุปกรณ์`
                  : 'ยังไม่มีข้อมูล'}
              </p>
            </article>

            <article className="summary-card">
              <span className="summary-label">
                POWERED ON
              </span>
              <strong>
                {smartHome ? poweredDevices : '—'}
              </strong>
              <p>อุปกรณ์ที่กำลังเปิดอยู่</p>
            </article>
          </section>

          <section className="content-grid">
            <article className="panel">
              <div className="panel-heading">
                <div>
                  <p className="section-kicker">
                    RUNTIME
                  </p>
                  <h2>System checks</h2>
                </div>

                <span
                  className={`status-pill ${
                    health === null
                      ? 'status-muted'
                      : health.status === 'healthy'
                        ? 'status-good'
                        : 'status-warning'
                  }`}
                >
                  {health?.status ?? 'unknown'}
                </span>
              </div>

              <div className="check-list">
                {health ? (
                  Object.entries(
                    health.checks,
                  ).map(([name, ready]) => (
                    <div
                      className="check-row"
                      key={name}
                    >
                      <span
                        className={`status-dot ${
                          ready
                            ? 'dot-good'
                            : 'dot-warning'
                        }`}
                        aria-hidden="true"
                      />
                      <span>
                        {formatCheckName(name)}
                      </span>
                      <strong>
                        {ready ? 'พร้อม' : 'ไม่พร้อม'}
                      </strong>
                    </div>
                  ))
                ) : (
                  <div className="empty-state">
                    <strong>
                      ไม่สามารถโหลดสถานะระบบ
                    </strong>
                    <p>
                      ระบบจะลองเชื่อมต่อใหม่อัตโนมัติ
                    </p>
                  </div>
                )}
              </div>
            </article>

            <article className="panel devices-panel">
              <div className="panel-heading">
                <div>
                  <p className="section-kicker">
                    TUYA DEVICES
                  </p>
                  <h2>Smart Home devices</h2>
                </div>

                <span className="read-only-badge">
                  READ ONLY
                </span>
              </div>

              {smartHome === null ? (
                <div className="empty-state">
                  <strong>
                    ไม่สามารถโหลดข้อมูล Smart Home
                  </strong>
                  <p>
                    ระบบจะลองเชื่อมต่อใหม่อัตโนมัติ
                  </p>
                </div>
              ) : smartHome.devices.length ? (
                <div className="device-grid">
                  {smartHome.devices.map((device) => (
                    <article
                      className="device-card"
                      key={device.id}
                    >
                      <div className="device-topline">
                        <span
                          className={`device-icon ${
                            device.power
                              ? 'device-active'
                              : ''
                          }`}
                          aria-hidden="true"
                        >
                          {device.device_type
                            .slice(0, 1)
                            .toUpperCase()}
                        </span>

                        <span
                          className={`status-pill ${
                            device.online
                              ? 'status-good'
                              : 'status-muted'
                          }`}
                        >
                          {device.online
                            ? 'Online'
                            : 'Offline'}
                        </span>
                      </div>

                      <div>
                        <h3>{device.name}</h3>
                        <p>
                          {device.room || 'ไม่ระบุห้อง'}
                        </p>
                      </div>

                      <div className="device-footer">
                        <span>สถานะพลังงาน</span>
                        <strong
                          className={
                            device.power
                              ? 'power-on'
                              : 'power-off'
                          }
                        >
                          {device.power ? 'เปิด' : 'ปิด'}
                        </strong>
                      </div>
                    </article>
                  ))}
                </div>
              ) : (
                <div className="empty-state">
                  <strong>ไม่พบอุปกรณ์</strong>
                  <p>
                    ยังไม่มีอุปกรณ์ Smart Home ที่แสดงได้
                  </p>
                </div>
              )}
            </article>
          </section>
        </>
      )}
    </main>
  )
}

export default App