//status
export async function fetchStatus(token) {
  const res = await fetch(`${import.meta.env.VITE_API_BASE_URL}/status`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  })

  if (!res.ok) throw new Error("Failed to fetch status")
  return await res.json()
}
//status/id
export async function fetchDeviceStatus(deviceId, token) {
  const res = await fetch(
    `${import.meta.env.VITE_API_BASE_URL}/status/${deviceId}`,
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
  const res = await fetch(`${import.meta.env.VITE_API_BASE_URL}/command/${deviceId}/plus`, {
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
  const res = await fetch(`${import.meta.env.VITE_API_BASE_URL}/command/${deviceId}/minus`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  })
  if (!res.ok) throw new Error("Failed to decrease target temp")
  return await res.json()
}
//  Set target temperature /command/{device_id}/set/{target_temp}
//set target temp
export async function setTargetTemp(deviceId, temp, token) {
  const res = await fetch(`${import.meta.env.VITE_API_BASE_URL}/command/${deviceId}/set/${temp}`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    // No need for body if temp is in URL
  })
  if (!res.ok) throw new Error("Failed to set target temp")
  return await res.json();
}
