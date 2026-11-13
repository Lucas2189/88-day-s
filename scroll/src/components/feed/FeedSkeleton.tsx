export function FeedSkeleton() {
  return (
    <div className="flex h-dvh flex-col" aria-busy="true" aria-label="Loading feed">
      <div style={{ height: "calc(var(--safe-top) + 56px)" }} />
      <div className="flex flex-1 items-center gap-1 px-2">
        <div className="skeleton h-[56%] w-full flex-1 rounded-2xl" />
        <div className="flex w-14 flex-col items-center gap-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="skeleton h-11 w-11 rounded-full" />
          ))}
        </div>
      </div>
      <div className="space-y-2 px-4 pt-3" style={{ paddingBottom: "calc(var(--tabbar-h) + var(--safe-bottom) + 12px)" }}>
        <div className="skeleton h-5 w-24 rounded-full" />
        <div className="skeleton h-5 w-3/4 rounded" />
        <div className="skeleton h-4 w-1/2 rounded" />
      </div>
    </div>
  );
}
