import React from "react"
import ReactDOM from "react-dom/client"
import App from "./App" // './enhance-page'에서 './App'으로 변경
import "./index.css"

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
