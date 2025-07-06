import { useState } from "react"
import { setTargetTemp } from "../services/apiService"

export default function DeviceControls({ deviceId, current, token, onDeviceUpdated }) {
  const [targetTemp, setTargetTempInput] = useState(current.target_temp)
  const [loading, setLoading] = useState(false)

  const handleChange = (delta) => setTargetTempInput((t) => t + delta)

  const handleAction = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      await setTargetTemp(deviceId, targetTemp, token)
      onDeviceUpdated(deviceId)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <h3 className="mb-4" style={{ fontSize: "1.5rem", fontWeight: 700 }}>
        Set target temperature
      </h3>
      <div className="d-flex justify-content-center align-items-center" style={{ minHeight: "1vh" }}>
        <form className="d-flex gap-2 align-items-center" onSubmit={handleAction}>
          <button type="button" className="btn btn-danger" disabled={loading} onClick={() => handleChange(-1)}>
            –
          </button>
          <input
            type="number"
            value={targetTemp}
            onChange={e => setTargetTempInput(Number(e.target.value))}
            min={0}
            max={40}
            className="form-control w-auto text-center"
            style={{ maxWidth: 80 }}
          />
          <button type="button" className="btn btn-success" disabled={loading} onClick={() => handleChange(1)}>
            +
          </button>
          <div>
            <button type="submit" className="btn btn-primary" disabled={loading}>
              Set
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}