import { useState, useEffect } from "react";

export const useTheme = () => {
  const savedTheme = localStorage.getItem("theme");
  const [isDarkMode, setIsDarkMode] = useState(savedTheme === "dark");

  useEffect(() => {
    if (isDarkMode) {
      document.body.classList.add("dark");
      localStorage.setItem("theme", "dark");
    } else {
      document.body.classList.remove("dark");
      localStorage.setItem("theme", "light");
    }
  }, [isDarkMode]);

  return { isDarkMode, setIsDarkMode };
};
