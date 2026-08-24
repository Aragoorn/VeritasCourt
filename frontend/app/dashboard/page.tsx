"use client";

import { useEffect, useState } from "react";
import api from "@/lib/api";
import { Claim } from "@/types";
import Link from "next/link";

export default function DashboardPage() {
  const [claims, setClaims] = useState<Claim[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get("/claims")
      .then((res) => setClaims(res.data))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const stats = {
    total: claims.length,
    resolved: claims.filter((c) => c.status === "AI_RESOLVED" || c.status === "FINALIZED").length,
    pending: claims.filter((c) => ["SUBMITTED", "AI_REVIEWING", "HUMAN_REVIEW"].includes(c.status)).length,
  };

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Dashboard Overview</h1>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white rounded-xl p-6 shadow-sm border">
          <p className="text-sm text-slate-500">Total Claims</p>
          <p className="text-3xl font-bold mt-1">{stats.total}</p>
        </div>
        <div className="bg-white rounded-xl p-6 shadow-sm border">
          <p className="text-sm text-slate-500">Resolved</p>
          <p className="text-3xl font-bold mt-1 text-green-600">{stats.resolved}</p>
        </div>
        <div className="bg-white rounded-xl p-6 shadow-sm border">
          <p className="text-sm text-slate-500">Pending</p>
          <p className="text-3xl font-bold mt-1 text-amber-600">{stats.pending}</p>
        </div>
      </div>

      <div className="flex justify-between items-center mb-4">
        <h2 className="text-lg font-semibold">Recent Claims</h2>
        <Link
          href="/dashboard/claims/new"
          className="px-4 py-2 bg-slate-900 text-white text-sm rounded-lg hover:bg-slate-800"
        >
          + New Claim
        </Link>
      </div>

      {loading ? (
        <p>Loading...</p>
      ) : (
        <div className="bg-white rounded-xl shadow-sm border overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-slate-50 border-b">
              <tr>
                <th className="text-left px-4 py-3">Title</th>
                <th className="text-left px-4 py-3">Status</th>
                <th className="text-left px-4 py-3">Created</th>
              </tr>
            </thead>
            <tbody>
              {claims.slice(0, 5).map((claim) => (
                <tr key={claim.id} className="border-b hover:bg-slate-50">
                  <td className="px-4 py-3">
                    <Link href={`/dashboard/claims/${claim.id}`} className="font-medium hover:underline">
                      {claim.title}
                    </Link>
                  </td>
                  <td className="px-4 py-3">
                    <span className="px-2 py-1 rounded-full text-xs bg-slate-100">
                      {claim.status}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-slate-500">
                    {new Date(claim.createdAt).toLocaleDateString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}