import { ReactNode } from "react";
import { SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar";
import { AppSidebar } from "./sidebar";
import { useAuth } from "@workspace/dreamco-auth-web";
import { Button } from "@/components/ui/button";
import { LogIn, LogOut } from "lucide-react";

function AuthBadge() {
  const { user, isLoading, isAuthenticated, login, logout } = useAuth();
  if (isLoading) return null;
  if (!isAuthenticated) {
    return (
      <Button onClick={login} size="sm" variant="outline" className="font-mono text-xs uppercase tracking-wider gap-2">
        <LogIn className="h-3.5 w-3.5" />
        Log in
      </Button>
    );
  }
  return (
    <div className="flex items-center gap-3">
      <div className="text-right">
        <div className="font-mono text-xs text-foreground leading-tight">
          {user?.firstName ?? user?.email ?? "operator"}
        </div>
        <div className="font-mono text-[10px] text-muted-foreground uppercase tracking-wider">
          authenticated
        </div>
      </div>
      {user?.profileImageUrl ? (
        <img src={user.profileImageUrl} alt="" className="w-8 h-8 rounded-sm border border-primary/30" />
      ) : (
        <div className="w-8 h-8 rounded-sm border border-primary/30 bg-primary/10 flex items-center justify-center font-mono text-xs text-primary">
          {(user?.firstName?.[0] ?? user?.email?.[0] ?? "?").toUpperCase()}
        </div>
      )}
      <Button onClick={logout} size="sm" variant="ghost" className="font-mono text-xs uppercase tracking-wider gap-1" title="Log out">
        <LogOut className="h-3.5 w-3.5" />
      </Button>
    </div>
  );
}

export function Layout({ children }: { children: ReactNode }) {
  return (
    <SidebarProvider>
      <div className="flex h-screen overflow-hidden bg-background w-full">
        <AppSidebar />
        <main className="flex-1 overflow-y-auto">
          <div className="h-14 border-b border-border/40 flex items-center px-4 gap-3">
            <SidebarTrigger className="md:hidden" />
            <div className="font-mono font-bold text-primary tracking-widest text-sm md:hidden">
              DREAMCO_OS //
            </div>
            <div className="ml-auto">
              <AuthBadge />
            </div>
          </div>
          <div className="p-6 md:p-8 h-full max-w-7xl mx-auto">
            {children}
          </div>
        </main>
      </div>
    </SidebarProvider>
  );
}
