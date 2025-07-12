import React from "react"
import ReactDOM from "react-dom/client"
import { PublicClientApplication } from "@azure/msal-browser"
import { MsalProvider } from "@azure/msal-react"
import { msalConfig } from "./auth/authConfig"
import Dashboard from "./views/Dashboard"
import 'bootstrap/dist/css/bootstrap.min.css'
import './custom.css'

const msalInstance = new PublicClientApplication(msalConfig)

async function bootstrap() {
  try {
    await msalInstance.initialize() 
    await msalInstance.handleRedirectPromise()

    ReactDOM.createRoot(document.getElementById("root")).render(
      <React.StrictMode>
        <MsalProvider instance={msalInstance}>
          <main className="bg-dark text-light">
            <Dashboard />
          </main>
        </MsalProvider>
      </React.StrictMode>
    )
  } catch (e) {
    console.error("MSAL startup error:", e)
  }
}

bootstrap()