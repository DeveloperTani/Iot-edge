import { useMsal, useIsAuthenticated } from "@azure/msal-react"
import { useEffect, useState, useCallback } from "react"
import { loginRequest } from "../auth/authConfig"
import { fetchStatus, fetchDeviceStatus } from "../services/apiService"
import StatusList from "../components/StatusList"

export default function Dashboard() {
  const { instance, accounts, inProgress } = useMsal()
  const isAuthenticated = useIsAuthenticated()
  const [statuses, setStatuses] = useState({})
  const [token, setToken] = useState(null)
  const [error, setError] = useState(null)

  // Handle login if not authenticated
  useEffect(() => {
    if (inProgress !== "none") return
    if (!isAuthenticated) {
      instance.loginRedirect(loginRequest)
    }
  }, [isAuthenticated, inProgress, instance])

  // Fetch all statuses (and token) if authenticated
  useEffect(() => {
    if (!isAuthenticated || accounts.length === 0) return

    async function fetchData() {
      try {
        const response = await instance.acquireTokenSilent({
          ...loginRequest,
          account: accounts[0],
        })
        setToken(response.accessToken)
        const data = await fetchStatus(response.accessToken)
        setStatuses(data)
      } catch (err) {
        setError("Failed to load device status")
        console.error(err)
      }
    }

    fetchData()
  }, [isAuthenticated, accounts, instance])

  // Per-device status refresh handler
  const refreshDeviceStatus = useCallback(async (deviceId) => {
    if (!token) return
    try {
      const deviceStatus = await fetchDeviceStatus(deviceId, token)
      setStatuses(prev => ({
        ...prev,
        [deviceId]: deviceStatus
      }))
    } catch (err) {
      setError("Failed to update device status")
      console.error(err)
    }
  }, [token])

console.log("Client ID:", import.meta.env.VITE_AZURE_CLIENT_ID)

  if (inProgress !== "none") return <div>Authenticating…</div>
  if (!isAuthenticated) return <div>Redirecting to sign in…</div>
  if (error) return <div className="text-red-500">Error: {error}</div>

  return (
    <main className="min-h-screen bg-gray-100 p-4">
      <StatusList
        statuses={statuses}
        onDeviceUpdated={refreshDeviceStatus}
        token={token}
      />
    </main>
  )
}