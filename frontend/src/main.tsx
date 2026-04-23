import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";

import { App } from "./App";
import { I18nProvider } from "./i18n";
import { AuthProvider } from "./store/auth.store";
import { UiProvider } from "./store/ui.store";
import "./styles/tokens.css";
import "./styles/layout.css";
import "./styles/components.css";
import "./styles/utilities.css";

const routerFuture = {
  v7_startTransition: true,
  v7_relativeSplatPath: true,
} as const;

ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(
  <BrowserRouter future={routerFuture}>
    <I18nProvider>
      <UiProvider>
        <AuthProvider>
          <App />
        </AuthProvider>
      </UiProvider>
    </I18nProvider>
  </BrowserRouter>,
);
