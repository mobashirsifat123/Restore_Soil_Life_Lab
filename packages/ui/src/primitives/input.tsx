import type { InputHTMLAttributes, TextareaHTMLAttributes } from "react";

import { cn } from "../lib/cn";

export function Input(props: InputHTMLAttributes<HTMLInputElement>) {
  return (
    <input
      className={cn(
        "w-full rounded-[18px] border border-[rgba(72,85,59,0.18)] bg-[#fffaf1] px-4 py-3 text-sm text-[#283422] outline-none transition-colors duration-base placeholder:text-[#87846f] focus:border-[#b97849] focus:ring-2 focus:ring-[rgba(185,120,73,0.18)]",
        props.className,
      )}
      {...props}
    />
  );
}

export function Textarea(props: TextareaHTMLAttributes<HTMLTextAreaElement>) {
  return (
    <textarea
      className={cn(
        "min-h-32 w-full rounded-[18px] border border-[rgba(72,85,59,0.18)] bg-[#fffaf1] px-4 py-3 text-sm text-[#283422] outline-none transition-colors duration-base placeholder:text-[#87846f] focus:border-[#b97849] focus:ring-2 focus:ring-[rgba(185,120,73,0.18)]",
        props.className,
      )}
      {...props}
    />
  );
}
