export default function MarketingLoading() {
  return (
    <div className="min-h-[60vh] bg-[#f5efdf] px-6 py-20">
      <div className="mx-auto max-w-[1100px] animate-pulse">
        <div className="h-5 w-40 rounded-full bg-[rgba(58,92,47,0.18)]" />
        <div className="mt-6 h-12 w-full max-w-[720px] rounded-2xl bg-[rgba(58,92,47,0.14)]" />
        <div className="mt-4 h-12 w-full max-w-[560px] rounded-2xl bg-[rgba(58,92,47,0.12)]" />
        <div className="mt-10 grid gap-4 md:grid-cols-3">
          {Array.from({ length: 3 }).map((_, index) => (
            <div
              key={`marketing-loading-card-${index}`}
              className="h-44 rounded-3xl bg-[rgba(58,92,47,0.1)]"
            />
          ))}
        </div>
      </div>
    </div>
  );
}
