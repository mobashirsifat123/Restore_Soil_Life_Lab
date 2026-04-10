import type { ButtonHTMLAttributes, PropsWithChildren } from "react";

import { cn } from "../lib/cn";

type ButtonVariant = "primary" | "secondary" | "ghost";

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
}

const variantClasses: Record<ButtonVariant, string> = {
  primary:
    "rounded-full bg-[#556347] px-5 text-[#f8f2e7] shadow-raised hover:bg-[#445139] disabled:bg-[#93a083]",
  secondary:
    "rounded-full border border-[rgba(72,85,59,0.16)] bg-[#fbf6ee] text-[#283422] hover:border-[#556347] hover:bg-[#f4ebdb]",
  ghost: "rounded-full text-[#283422] hover:bg-[rgba(72,85,59,0.08)]",
};

export function Button({
  children,
  className,
  type = "button",
  variant = "primary",
  ...props
}: PropsWithChildren<ButtonProps>) {
  const resolvedVariant: ButtonVariant = variant;

  return (
    <button
      className={cn(
        "inline-flex items-center justify-center px-4 py-2.5 text-sm font-semibold transition-colors duration-base disabled:cursor-not-allowed disabled:opacity-60",
        variantClasses[resolvedVariant],
        className,
      )}
      type={type}
      {...props}
    >
      {children}
    </button>
  );
}
