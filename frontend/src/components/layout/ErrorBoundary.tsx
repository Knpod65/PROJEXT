import { Component, type ErrorInfo, type ReactNode } from "react";

interface ErrorBoundaryProps {
  children: ReactNode;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

/**
 * Class-based error boundary. Wraps the protected app layout outlet so that
 * a runtime error in any page component shows a recovery screen instead of
 * crashing the entire application.
 *
 * Hooks cannot catch render-phase errors, so this must remain a class component.
 */
export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    // Forward to a real error reporting service (e.g. Sentry) once integrated.
    console.error("[EMS] Unhandled component error:", error, info.componentStack);
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null });
  };

  render() {
    if (this.state.hasError) {
      return (
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            minHeight: "60vh",
            padding: "2rem",
          }}
        >
          <div
            style={{
              textAlign: "center",
              maxWidth: "420px",
              display: "flex",
              flexDirection: "column",
              gap: "12px",
            }}
          >
            <span style={{ fontSize: "2rem" }} aria-hidden="true">⚠</span>
            <h2 style={{ margin: 0 }}>Something went wrong</h2>
            <p style={{ margin: 0, color: "var(--text-mid, #666)" }}>
              An unexpected error occurred on this page. Your session is still active
              — you can try again or navigate to another section.
            </p>
            {this.state.error ? (
              <p
                style={{
                  margin: 0,
                  fontSize: "0.8rem",
                  color: "var(--text-mid, #888)",
                  fontFamily: "monospace",
                }}
              >
                {this.state.error.message}
              </p>
            ) : null}
            <div style={{ display: "flex", gap: "8px", justifyContent: "center", marginTop: "8px" }}>
              <button
                className="ui-button ui-button--outline ui-button--md"
                type="button"
                onClick={this.handleReset}
              >
                Try again
              </button>
              <a className="ui-button ui-button--ghost ui-button--md" href="/dashboard">
                Go to dashboard
              </a>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
