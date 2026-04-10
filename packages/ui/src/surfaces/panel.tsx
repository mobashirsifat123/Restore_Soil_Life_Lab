import type { ComponentPropsWithoutRef, PropsWithChildren } from "react";

import { cn } from "../lib/cn";

export function Panel({
  children,
  className,
  ...props
}: PropsWithChildren<ComponentPropsWithoutRef<"section">>) {
  return (
    <section
      className={cn(
        "bg-organic-card rounded-[28px] border border-[rgba(72,85,59,0.14)] p-6 shadow-flat backdrop-blur-sm",
        className,
      )}
      {...props}
    >
      {children}
    </section>
  );
}
