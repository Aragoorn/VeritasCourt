import Link from "next/link";

export default function NotFound() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center gap-4">
      <h1 className="text-4xl font-bold">404</h1>
      <p className="text-slate-500">Page not found</p>
      <Link href="/" className="text-slate-900 underline">
        Go back home
      </Link>
    </div>
  );
}