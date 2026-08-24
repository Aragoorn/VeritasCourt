"use client";

import { useAuth } from "@/lib/auth";

export default function Header({ title }: { title?: string }) {
  const { user } = useAuth();

  return (
    <header className="flex items-center justify-between mb-8">
      <div>
        {title && <h1 className="text-2xl font-bold text-slate-900">{title}</h1>}
      </div>
      <div className="flex items-center gap-3">
        <div className="text-right">
          <p className="text-sm font-medium text-slate-900">{user?.name || "User"}</p>
          <p className="text-xs text-slate-500">{user?.role}</p>
        </div>
        <div className="w-9 h-9 rounded-full bg-slate-200 flex items-center justify-center text-sm font-medium text-slate-700">
          {(user?.name || user?.email || "U").charAt(0).toUpperCase()}
        </div>
      </div>
    </header>
  );
}