import { useEffect, useState } from "react";
import axios from "axios";
import { Textarea } from "@/components/textarea.jsx";
import { Button } from "@/components/ui/button";
import { Copy, Loader2Icon } from "lucide-react";
import { CopyButton } from "@/components/ui/copybutton";
import { ThemeToggle } from "@/components/ui/theme-toggle";
import { useTheme } from "@/lib/useTheme";

export default function App() {
  const [input, setInput] = useState("");
  const [chat, setChat] = useState("");
  const [isPendingResponse, setIsPendingResponse] = useState(false);
  const { isDarkMode, setIsDarkMode } = useTheme();

  useEffect(() => {
    console.log(input);
  });

  const sendMessage = async () => {
    if (isPendingResponse) return;

    try {
      setIsPendingResponse(true);
      const res = await axios.post("http://127.0.0.1:8000/chat", {
        message: input,
      });
      setChat(res.data.response);
    } catch (err) {
      console.error("Error:", err);
      setChat("Error occurred.");
    } finally {
      setIsPendingResponse(false);
    }
  };

  return (
    <div className="p-6 min-h-screen bg-white dark:bg-gray-900 text-black dark:text-white">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-3xl font-extrabold">RFP Chat</h1>
        <ThemeToggle />
      </div>

      <label htmlFor="user-input" className="sr-only">
        Type your question here
      </label>
      <Textarea
        id="user-input"
        name="userInput"
        onChange={(e) => setInput(e.target.value)}
        placeholder="Type your question here"
      ></Textarea>
      <Button
        onClick={sendMessage}
        className="mt-2 cursor-pointer disabled:cursor-not-allowed"
        size="lg"
        disabled={isPendingResponse}
      >
        {isPendingResponse ? (
          <>
            <Loader2Icon className="animate-spin" />
            Please wait
          </>
        ) : (
          <>Ask</>
        )}
      </Button>
      <div className="flex mt-4 gap-2 justify-between items-center">
        <div className="whitespace-pre-wrap">{chat}</div>
        <CopyButton text={chat} disabled={!chat} />
      </div>
    </div>
  );
}
