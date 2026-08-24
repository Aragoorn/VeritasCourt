"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import api from "@/lib/api";
import { Claim } from "@/types";

export default function ClaimsPage() {
  const [claims, setClaims] = useState<Claim[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get("/claims")
      .then((res) => setClaims(res.data))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">All Claims</h1>
        <Link
          href="/dashboard/claims/new"
          className="px-4 py-2 bg-slate-900 text-white text-sm rounded-lg hover:bg-slate-800"
        >
          + New Claim
        </Link>
      </div>

      {loading ? (
        <p>Loading...</p>
      ) : claims.length === 0 ? (
        <p className="text-slate-500">No claims yet.</p>
      ) : (
        <div className="grid gap-4">
          {claims.map((claim) => (
            <Link
              key={claim.id}
              href={`/dashboard/claims/${claim.id}`}
              className="block bg-white border rounded-xl p-5 hover:shadow-md transition"
            >
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="font-semibold text-lg">{claim.title}</h3>
                  <p className="text-sm text-slate-500 mt-1 line-clamp-2">{claim.description}</p>
                </div>
                <span className="px-2.5 py-1 rounded-full text-xs font-medium bg-slate-100">
                  {claim.status}
                </span>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}