//status
export async function fetchStatus(token) {
  const res = await fetch(`${import.meta.env.VITE_API_BASE_URL}/mqtt/status`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  })

  if (!res.ok) throw new Error("Failed to fetch status")
  return await res.json()
}
//mqtt/status/id
export async function fetchDeviceStatus(deviceId, token) {
  const res = await fetch(
    `${import.meta.env.VITE_API_BASE_URL}/mqtt/status/${deviceId}`,
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  )
  if (!res.ok) throw new Error("Failed to fetch device status")
  return await res.json()
}
//increase temp
export async function increase(deviceId, token) {
  const res = await fetch(`${import.meta.env.VITE_API_BASE_URL}/mqtt/commands/${deviceId}/increase`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  })
  if (!res.ok) throw new Error("Failed to increase target temp")
  return await res.json()
}
//decrease temp
export async function decrease(deviceId, token) {
  const res = await fetch(`${import.meta.env.VITE_API_BASE_URL}/mqtt/commands/${deviceId}/decrease`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  })
  if (!res.ok) throw new Error("Failed to decrease target temp")
  return await res.json()
}
//  Set target temperature mqtt/command/{device_id}/set/{target_temp}
//set target temp
export async function setTargetTemp(deviceId, temp, token) {
  const res = await fetch(`${import.meta.env.VITE_API_BASE_URL}/mqtt/commands/${deviceId}/set/${temp}`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },

  })
  if (!res.ok) throw new Error("Failed to set target temp")
  return await res.json();
}
