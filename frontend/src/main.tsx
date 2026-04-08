import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";

import { App } from "./App";
import { AuthProvider } from "./store/auth.store";
import { UiProvider } from "./store/ui.store";
import "./styles/tokens.css";
import "./styles/layout.css";
import "./styles/components.css";
import "./styles/utilities.css";

ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(
  <BrowserRouter>
    <UiProvider>
      <AuthProvider>
        <App />
      </AuthProvider>
    </UiProvider>
  </BrowserRouter>,
);
