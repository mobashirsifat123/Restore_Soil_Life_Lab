export default function PlatformLoading() {
  return (
    <div className="min-h-[55vh] px-6 py-10">
      <div className="mx-auto max-w-[1280px] animate-pulse">
        <div className="h-8 w-72 rounded-2xl bg-[rgba(58,92,47,0.16)]" />
        <div className="mt-8 grid gap-5 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, index) => (
            <div
              key={`platform-loading-card-${index}`}
              className="h-32 rounded-2xl border border-[rgba(58,92,47,0.12)] bg-white/70"
            />
          ))}
        </div>
      </div>
    </div>
  );
}
