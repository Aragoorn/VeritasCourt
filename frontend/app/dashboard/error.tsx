"use client";

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div className="flex flex-col items-center justify-center h-64 gap-4">
      <h2 className="text-lg font-semibold text-slate-900">Something went wrong</h2>
      <p className="text-sm text-slate-500">{error.message}</p>
      <button
        onClick={reset}
        className="px-4 py-2 bg-slate-900 text-white text-sm rounded-lg hover:bg-slate-800"
      >
        Try again
      </button>
    </div>
  );
}