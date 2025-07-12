export const msalConfig = {
  auth: {
    clientId: import.meta.env.VITE_AZURE_CLIENT_ID,
    authority: `https://login.microsoftonline.com/${import.meta.env.VITE_AZURE_TENANT_ID}`,
    redirectUri: window.location.origin,
  },
  cache: {
    cacheLocation: "localStorage",
    storeAuthStateInCookie: false,
  },
}
console.log("Client ID:", import.meta.env.VITE_AZURE_CLIENT_ID);
console.log("Tenant ID:", import.meta.env.VITE_AZURE_TENANT_ID);
console.log("API Scope:", import.meta.env.VITE_API_SCOPE);

export const loginRequest = {
  scopes: [import.meta.env.VITE_API_SCOPE],
}