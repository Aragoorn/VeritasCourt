import Link from "next/link";

export default function HomePage() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-slate-900 to-slate-800 text-white">
      <div className="text-center space-y-6 max-w-2xl px-4">
        <h1 className="text-5xl font-bold tracking-tight">Veritas</h1>
        <p className="text-xl text-slate-300">
          Enterprise Hybrid AI + Human Claim & Dispute Resolution Platform
        </p>
        <div className="flex gap-4 justify-center mt-8">
          <Link
            href="/login"
            className="px-6 py-3 bg-white text-slate-900 rounded-lg font-medium hover:bg-slate-100 transition"
          >
            Login
          </Link>
          <Link
            href="/register"
            className="px-6 py-3 border border-white/30 rounded-lg font-medium hover:bg-white/10 transition"
          >
            Register
          </Link>
        </div>
      </div>
    </div>
  );
}