export default function Loading() {
  return (
    <div className="space-y-4">
      {[1, 2, 3].map((i) => (
        <div key={i} className="h-24 bg-slate-100 animate-pulse rounded-xl" />
      ))}
    </div>
  );
}