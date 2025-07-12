import React from "react"
import ReactDOM from "react-dom/client"
import { PublicClientApplication } from "@azure/msal-browser"
import { MsalProvider } from "@azure/msal-react"
import { msalConfig } from "./auth/authConfig"


const msalInstance = new PublicClientApplication(msalConfig)

async function bootstrap() {
  try {
    await msalInstance.initialize() 
    await msalInstance.handleRedirectPromise().catch((e) => {
  if (e.errorCode !== "no_token_request_cache_error") {
    console.error("MSAL startup error:", e)
  }
})

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