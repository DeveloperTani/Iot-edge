import React from "react"
import ReactDOM from "react-dom/client"
import { PublicClientApplication } from "@azure/msal-browser"
import { MsalProvider } from "@azure/msal-react"
import { msalConfig } from "./auth/authConfig"
import Dashboard from "./views/Dashboard"
import 'bootstrap/dist/css/bootstrap.min.css'
import './custom.css'

const msalInstance = new PublicClientApplication(msalConfig)

msalInstance.handleRedirectPromise().then(() => {
  ReactDOM.createRoot(document.getElementById("root")).render(
    <React.StrictMode>
      <MsalProvider instance={msalInstance}>
        <body className="bg-dark text-light">
          <Dashboard />
        </body>
      </MsalProvider>
    </React.StrictMode>
  )
}).catch((error) => {
  console.error("Error handling redirect:", error)
})