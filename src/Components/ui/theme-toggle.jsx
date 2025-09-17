import { Button } from "@/components/ui/button"; // shadcn button
import { Moon, Sun } from "lucide-react";
import { useTheme } from "@/lib/useTheme";

export function ThemeToggle() {
  const { isDarkMode, setIsDarkMode } = useTheme();

  return (
    <Button
      variant="outline"
      size="icon"
      onClick={() => setIsDarkMode(!isDarkMode)}
    >
      {isDarkMode ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
    </Button>
  );
}
