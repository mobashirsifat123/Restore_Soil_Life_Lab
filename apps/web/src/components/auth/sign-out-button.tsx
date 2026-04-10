"use client";

type SignOutButtonProps = {
  className?: string;
  label?: string;
  redirectTo?: string;
};

export function SignOutButton({
  className,
  label = "Sign out",
  redirectTo = "/",
}: SignOutButtonProps) {
  const href = `/logout?redirect=${encodeURIComponent(redirectTo)}`;

  return (
    <a href={href} className={className}>
      {label}
    </a>
  );
}
