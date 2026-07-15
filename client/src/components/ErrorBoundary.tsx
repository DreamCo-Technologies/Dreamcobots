import { Component, type ReactNode } from "react";
import { Button } from "@/components/ui/button";
import { AlertTriangle, RefreshCw, Home } from "lucide-react";

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
  pageName?: string;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, info: { componentStack: string }) {
    console.error("[ErrorBoundary] Caught error:", error.message, info.componentStack);
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null });
  };

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) return this.props.fallback;
      return (
        <div className="flex flex-col items-center justify-center min-h-[400px] p-8 text-center">
          <div className="h-16 w-16 rounded-2xl bg-destructive/10 flex items-center justify-center mb-4">
            <AlertTriangle className="h-8 w-8 text-destructive" />
          </div>
          <h2 className="text-xl font-bold mb-2">
            {this.props.pageName ? `${this.props.pageName} failed to load` : "Something went wrong"}
          </h2>
          <p className="text-sm text-muted-foreground mb-2 max-w-md">
            {this.state.error?.message ?? "An unexpected error occurred while rendering this page."}
          </p>
          <p className="text-xs text-muted-foreground/60 mb-6">
            Try refreshing this section or navigate to another page. Other modules are unaffected.
          </p>
          <div className="flex items-center gap-3">
            <Button variant="outline" size="sm" onClick={this.handleReset} data-testid="button-retry-error">
              <RefreshCw className="h-3.5 w-3.5 mr-2" /> Retry
            </Button>
            <Button size="sm" onClick={() => { window.location.href = "/dashboard"; }} data-testid="button-go-dashboard">
              <Home className="h-3.5 w-3.5 mr-2" /> Dashboard
            </Button>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}

export default ErrorBoundary;
