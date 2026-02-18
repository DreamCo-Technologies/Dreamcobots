import { useEffect, useMemo, useState } from "react";
import { Button } from "@/components/ui/button";
import { Moon, Sun } from "lucide-react";

type Theme = "light" | "dark";

function getInitialTheme(): Theme {
  const saved = localStorage.getItem("buddy.theme");
  if (saved === "light" || saved === "dark") return saved;
  return "dark";
}

export default function ThemeToggle() {
  const [theme, setTheme] = useState<Theme>(() => getInitialTheme());

  const nextTheme = useMemo<Theme>(() => (theme === "dark" ? "light" : "dark"), [theme]);

  useEffect(() => {
    const root = document.documentElement;
    if (theme === "dark") root.classList.add("dark");
    else root.classList.remove("dark");
    localStorage.setItem("buddy.theme", theme);
  }, [theme]);

  return (
    <Button
      variant="outline"
      onClick={() => setTheme(nextTheme)}
      className="group relative h-10 w-10 rounded-xl border-border/70 bg-card/60 backdrop-blur hover:bg-card shadow-sm hover:shadow-md transition-all"
      aria-label="Toggle theme"
      data-testid="theme-toggle"
    >
      <Sun className="h-4 w-4 rotate-0 scale-100 transition-all duration-300 group-hover:scale-110 dark:-rotate-90 dark:scale-0" />
      <Moon className="absolute h-4 w-4 rotate-90 scale-0 transition-all duration-300 group-hover:scale-110 dark:rotate-0 dark:scale-100" />
    </Button>
  );
}
