"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import api from "@/lib/api";
import { Claim } from "@/types";
import toast from "react-hot-toast";
import Link from "next/link";

export default function ClaimDetailPage() {
  const { id } = useParams();
  const [claim, setClaim] = useState<Claim | null>(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [reason, setReason] = useState("");

  const fetchClaim = async () => {
    try {
      const res = await api.get(`/claims/${id}`);
      setClaim(res.data);
    } catch {
      toast.error("Failed to load claim");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (id) fetchClaim();
  }, [id]);

  const runAction = async (fn: () => Promise<any>, successMsg: string) => {
    setActionLoading(true);
    try {
      await fn();
      toast.success(successMsg);
      fetchClaim();
    } catch (err: any) {
      toast.error(err?.response?.data?.message || "Action failed");
    } finally {
      setActionLoading(false);
    }
  };

  if (loading) return <p>Loading...</p>;
  if (!claim) return <p>Claim not found</p>;

  return (
    <div className="max-w-4xl">
      <Link href="/dashboard/claims" className="text-sm text-slate-500 hover:underline mb-4 inline-block">
        ← Back to Claims
      </Link>

      <div className="bg-white border rounded-xl p-6 mb-6">
        <div className="flex justify-between items-start mb-4">
          <h1 className="text-2xl font-bold">{claim.title}</h1>
          <span className="px-3 py-1 rounded-full text-sm font-medium bg-slate-100">
            {claim.status}
          </span>
        </div>
        <p className="text-slate-700 whitespace-pre-wrap mb-4">{claim.description}</p>
        <div className="text-sm text-slate-500 space-y-1">
          <p>Created: {new Date(claim.createdAt).toLocaleString()}</p>
          {claim.genlayerClaimId && <p>GenLayer ID: {claim.genlayerClaimId}</p>}
          {claim.creator && <p>Creator: {claim.creator.name || claim.creator.email}</p>}
        </div>
      </div>

      {claim.evidence && claim.evidence.length > 0 && (
        <div className="bg-white border rounded-xl p-6 mb-6">
          <h2 className="font-semibold mb-3">Evidence</h2>
          <ul className="space-y-2">
            {claim.evidence.map((ev) => (
              <li key={ev.id}>
                <a href={ev.url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline text-sm">
                  {ev.fileName || ev.url}
                </a>
              </li>
            ))}
          </ul>
        </div>
      )}

      {claim.aiResolution && (
        <div className="bg-white border rounded-xl p-6 mb-6">
          <h2 className="font-semibold mb-3">AI Resolution</h2>
          <div className="space-y-2 text-sm">
            <p>
              <span className="font-medium">Decision:</span>{" "}
              <span className="font-bold">{claim.aiResolution.decision}</span>
            </p>
            <p>
              <span className="font-medium">Confidence:</span> {claim.aiResolution.confidence}%
            </p>
            {claim.aiResolution.reasoning && (
              <p>
                <span className="font-medium">Reasoning:</span> {claim.aiResolution.reasoning}
              </p>
            )}
          </div>
        </div>
      )}

      <div className="bg-white border rounded-xl p-6 space-y-4">
        <h2 className="font-semibold">Actions</h2>

        {(claim.status === "SUBMITTED" ||
          claim.status === "AI_REVIEWING" ||
          claim.status === "CHALLENGED" ||
          claim.status === "APPEALED") && (
          <button
            onClick={() => runAction(() => api.post(`/claims/${id}/resolve`), "AI resolve completed")}
            disabled={actionLoading}
            className="px-4 py-2 bg-green-600 text-white rounded-lg text-sm hover:bg-green-700 disabled:opacity-50"
          >
            Run AI Resolve
          </button>
        )}

        {claim.status === "AI_RESOLVED" && (
          <>
            <div>
              <label className="block text-sm font-medium mb-1">Reason (for Challenge / Appeal)</label>
              <textarea
                rows={3}
                value={reason}
                onChange={(e) => setReason(e.target.value)}
                className="w-full border rounded-lg px-3 py-2 text-sm"
                placeholder="Minimum 30 characters"
              />
            </div>
            <div className="flex flex-wrap gap-3">
              <button
                onClick={() =>
                  runAction(
                    () => api.post(`/claims/${id}/challenge`, { reason }),
                    "Challenge submitted",
                  )
                }
                disabled={actionLoading || reason.length < 30}
                className="px-4 py-2 bg-amber-600 text-white rounded-lg text-sm hover:bg-amber-700 disabled:opacity-50"
              >
                Challenge
              </button>
              <button
                onClick={() =>
                  runAction(
                    () => api.post(`/claims/${id}/appeal`, { reason }),
                    "Appeal submitted",
                  )
                }
                disabled={actionLoading || reason.length < 30}
                className="px-4 py-2 bg-orange-600 text-white rounded-lg text-sm hover:bg-orange-700 disabled:opacity-50"
              >
                Appeal
              </button>
              <button
                onClick={() =>
                  runAction(() => api.post(`/review/${id}/request`), "Sent to human review")
                }
                disabled={actionLoading}
                className="px-4 py-2 bg-slate-800 text-white rounded-lg text-sm hover:bg-slate-900 disabled:opacity-50"
              >
                Request Human Review
              </button>
              <button
                onClick={() =>
                  runAction(() => api.post(`/claims/${id}/finalize`), "Claim finalized")
                }
                disabled={actionLoading}
                className="px-4 py-2 bg-emerald-700 text-white rounded-lg text-sm hover:bg-emerald-800 disabled:opacity-50"
              >
                Finalize
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}