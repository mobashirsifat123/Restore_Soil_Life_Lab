import type { PropsWithChildren, ReactNode } from "react";

export function PageHeader({
  title,
  eyebrow,
  actions,
  children,
}: PropsWithChildren<{
  title: string;
  eyebrow?: string;
  actions?: ReactNode;
}>) {
  return (
    <header className="flex flex-col gap-5 pb-6 md:flex-row md:items-end md:justify-between">
      <div className="space-y-3">
        {eyebrow ? <p className="editorial-kicker font-mono text-xs">{eyebrow}</p> : null}
        <h1 className="font-serif text-4xl tracking-[-0.03em] text-[#283422] md:text-5xl">
          {title}
        </h1>
        {children ? (
          <div className="max-w-3xl text-base leading-7 text-[#5d624e]">{children}</div>
        ) : null}
      </div>
      {actions ? <div className="flex flex-wrap items-center gap-3">{actions}</div> : null}
    </header>
  );
}
