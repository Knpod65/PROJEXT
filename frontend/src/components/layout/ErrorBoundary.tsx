import React from "react";

import { Icon } from "@/components/ui/Icon";
import { translate } from "@/i18n";
import { withAppBasePath } from "@/utils/appPaths";

interface ErrorBoundaryProps {
  children: React.ReactNode;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, info: React.ErrorInfo) {
    console.error("[EMS] Unhandled component error:", error, info.componentStack);
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null });
  };

  render() {
    if (!this.state.hasError) return this.props.children;

    return (
      <div className="error-boundary">
        <div className="error-boundary__content">
          <span className="error-boundary__icon" aria-hidden="true"><Icon name="error" /></span>
          <h2>{translate("layout.errorBoundary.title")}</h2>
          <p>{translate("layout.errorBoundary.description")}</p>
          {this.state.error ? <p className="error-boundary__detail">{this.state.error.message}</p> : null}
          <div className="error-boundary__actions">
            <button className="ui-button ui-button--outline ui-button--md" type="button" onClick={this.handleReset}>
              {translate("common.tryAgain")}
            </button>
            <a className="ui-button ui-button--ghost ui-button--md" href={withAppBasePath("/dashboard")}>
              {translate("common.goToDashboard")}
            </a>
          </div>
        </div>
      </div>
    );
  }
}
