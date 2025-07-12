import React from "react"
import ReactDOM from "react-dom/client"
import { PublicClientApplication } from "@azure/msal-browser"
import { MsalProvider } from "@azure/msal-react"
import { msalConfig } from "./auth/authConfig"


const msalInstance = new PublicClientApplication(msalConfig)

msalInstance.handleRedirectPromise().then(() => {
  ReactDOM.createRoot(document.getElementById("root")).render(
    <React.StrictMode>
      <MsalProvider instance={msalInstance}>
        <App />
      </MsalProvider>
    </React.StrictMode>
  )
}).catch(error => {
  console.error("MSAL redirect error:", error)
})