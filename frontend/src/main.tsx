import ReactDOM from "react-dom/client";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
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

const queryClient = new QueryClient();

ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(
  <QueryClientProvider client={queryClient}>
    <BrowserRouter future={routerFuture}>
      <I18nProvider>
        <UiProvider>
          <AuthProvider>
            <App />
          </AuthProvider>
        </UiProvider>
      </I18nProvider>
    </BrowserRouter>
  </QueryClientProvider>,
);
