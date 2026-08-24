"use client";

import { useEffect, useState } from "react";
import api from "@/lib/api";
import { Claim } from "@/types";
import toast from "react-hot-toast";
import Link from "next/link";

export default function ReviewPage() {
  const [claims, setClaims] = useState<Claim[]>([]);
  const [loading, setLoading] = useState(true);
  const [submittingId, setSubmittingId] = useState<string | null>(null);
  const [notes, setNotes] = useState<Record<string, string>>({});

  const fetchPending = async () => {
    try {
      const res = await api.get("/review/pending");
      setClaims(res.data);
    } catch (err) {
      toast.error("Failed to load pending reviews");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPending();
  }, []);

  const handleSubmitReview = async (claimId: string, decision: string) => {
    setSubmittingId(claimId);
    try {
      await api.post(`/review/${claimId}/submit`, {
        decision,
        note: notes[claimId] || "",
      });
      toast.success(`Claim marked as ${decision}`);
      fetchPending();
    } catch (err: any) {
      toast.error(err?.response?.data?.message || "Submit failed");
    } finally {
      setSubmittingId(null);
    }
  };

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Human Review Queue</h1>

      {loading ? (
        <p>Loading...</p>
      ) : claims.length === 0 ? (
        <div className="bg-white border rounded-xl p-8 text-center text-slate-500">
          No claims waiting for human review.
        </div>
      ) : (
        <div className="space-y-6">
          {claims.map((claim) => (
            <div key={claim.id} className="bg-white border rounded-xl p-6">
              <div className="flex justify-between items-start mb-3">
                <div>
                  <Link href={`/dashboard/claims/${claim.id}`} className="text-lg font-semibold hover:underline">
                    {claim.title}
                  </Link>
                  <p className="text-sm text-slate-500 mt-1 line-clamp-2">{claim.description}</p>
                </div>
                <span className="px-2.5 py-1 rounded-full text-xs bg-amber-100 text-amber-800">
                  {claim.status}
                </span>
              </div>

              {claim.aiResolution && (
                <div className="bg-slate-50 rounded-lg p-3 mb-4 text-sm">
                  <p>
                    <span className="font-medium">AI Decision:</span> {claim.aiResolution.decision}{" "}
                    ({claim.aiResolution.confidence}%)
                  </p>
                  {claim.aiResolution.reasoning && (
                    <p className="mt-1 text-slate-600">{claim.aiResolution.reasoning}</p>
                  )}
                </div>
              )}

              <div className="mb-3">
                <label className="block text-sm font-medium mb-1">Review Note (optional)</label>
                <textarea
                  rows={2}
                  value={notes[claim.id] || ""}
                  onChange={(e) => setNotes({ ...notes, [claim.id]: e.target.value })}
                  className="w-full border rounded-lg px-3 py-2 text-sm"
                  placeholder="Add your review notes..."
                />
              </div>

              <div className="flex gap-3">
                <button
                  onClick={() => handleSubmitReview(claim.id, "APPROVED")}
                  disabled={submittingId === claim.id}
                  className="px-4 py-2 bg-green-600 text-white text-sm rounded-lg hover:bg-green-700 disabled:opacity-50"
                >
                  Approve
                </button>
                <button
                  onClick={() => handleSubmitReview(claim.id, "REJECTED")}
                  disabled={submittingId === claim.id}
                  className="px-4 py-2 bg-red-600 text-white text-sm rounded-lg hover:bg-red-700 disabled:opacity-50"
                >
                  Reject
                </button>
                <button
                  onClick={() => handleSubmitReview(claim.id, "PARTIAL")}
                  disabled={submittingId === claim.id}
                  className="px-4 py-2 bg-amber-600 text-white text-sm rounded-lg hover:bg-amber-700 disabled:opacity-50"
                >
                  Partial
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}