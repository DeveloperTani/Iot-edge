import DeviceControls from "./DeviceControls"

export default function StatusList({ statuses, onDeviceUpdated, token }) {
  if (!statuses || !Object.keys(statuses).length) return <div>Loading...</div>
  return (
    <div className="container py-5">
      <h2 className="text-center mb-4">Devices</h2>
      <div className="row justify-content-center">
        {Object.entries(statuses).map(([deviceId, status]) => (
          <div className="col-md-8 col-lg-6 mb-4" key={deviceId}>
            <div className="card card-bg shadow text-center mx-auto text-white" style={{ maxWidth: 520, fontSize: "1.1rem" }}>
              <div className="card-body">
                <h3 className="card-title mb-5" style={{ fontSize: "2rem", fontWeight: 700, letterSpacing: 1 }}>{deviceId}</h3>
                <ul className="list-unstyled mb-3">
                  <li><strong>Temp:</strong> <span style={{ fontSize: "1.4em" }}>{status.temperature} °C</span></li>
                  <li><strong>Humidity:</strong> {status.humidity} %</li>
                  <li><strong>Heating:</strong> {status.heating}</li>
                  <li><strong>Target Temp:</strong> {status.target_temp}</li>
                  <li className="text-secondary mt-2" style={{ fontSize: "0.95em" }}>
                    Last updated: <br />
                    {new Date(status.timestamp).toLocaleString()}
                  </li>
                </ul>
                <div className="mt-5 mb-4 px-3 py-2">
                <DeviceControls
                  deviceId={deviceId}
                  current={status}
                  token={token}
                  onDeviceUpdated={onDeviceUpdated}
                />
                </div>               
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}