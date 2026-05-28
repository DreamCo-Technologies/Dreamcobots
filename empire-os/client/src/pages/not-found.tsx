import { Link } from "wouter";
import Seo from "@/components/Seo";
import { Button } from "@/components/ui/button";
import { Compass } from "lucide-react";

export default function NotFound() {
  return (
    <div className="min-h-screen buddy-glow">
      <Seo title="DreamCo Empire OS — Not Found" description="The page you requested could not be found." />
      <div className="buddy-container py-10 md:py-16">
        <div className="buddy-card buddy-noise rounded-3xl border-border/60 p-10 md:p-12 text-center max-w-2xl mx-auto">
          <div className="mx-auto h-12 w-12 rounded-2xl bg-gradient-to-br from-primary/18 via-accent/10 to-transparent border border-border/60 shadow-sm flex items-center justify-center text-primary">
            <Compass className="h-6 w-6" />
          </div>
          <h1 className="mt-5 text-3xl md:text-4xl">Page not found</h1>
          <p className="mt-3 text-muted-foreground">
            The route doesn't exist. Head back to the Empire.
          </p>

          <div className="mt-7 flex items-center justify-center gap-3 flex-col sm:flex-row">
            <Link href="/" className="w-full sm:w-auto" data-testid="notfound-home-link">
              <Button className="w-full sm:w-auto rounded-xl">
                Go to Chat
              </Button>
            </Link>
            <Link href="/dashboard" className="w-full sm:w-auto" data-testid="notfound-dashboard-link">
              <Button variant="outline" className="w-full sm:w-auto rounded-xl">
                Dashboard
              </Button>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
