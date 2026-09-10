# JarvisAI Dashboard

Read-only web dashboard for monitoring the JarvisAI runtime and Smart Home devices.

## Development

Start the JarvisAI API from the repository root:

```powershell
jarvis api
```

Start the React development server in another terminal:

```powershell
npm run dev --prefix dashboard
```

Open <http://localhost:5173>.

Both processes must remain running during frontend development.

## Production

Build the dashboard:

```powershell
npm run build --prefix dashboard
```

Start the JarvisAI API:

```powershell
jarvis api
```

Open <http://127.0.0.1:8000>.

The production dashboard and API run from the same process.

## Validation

```powershell
npm run lint --prefix dashboard
npm run build --prefix dashboard
```

## Safety boundary

The dashboard currently provides read-only monitoring only.

It does not expose Smart Home turn-on, turn-off, or toggle controls.