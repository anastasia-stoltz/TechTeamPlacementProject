import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Check, Copy } from "lucide-react";

function CopyButton({ text, disabled }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    if (disabled) return;
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500); // reset after 1.5s
    } catch (err) {
      console.error("Failed to copy:", err);
    }
  };

  return (
    <Button
      variant="outline"
      size="icon"
      onClick={handleCopy}
      disabled={disabled}
      className="h-8 w-8 disabled:opacity-50 disabled:cursor-not-allowed"
    >
      {copied ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
      <span className="sr-only">Copy to clipboard</span>
    </Button>
  );
}

export { CopyButton };
