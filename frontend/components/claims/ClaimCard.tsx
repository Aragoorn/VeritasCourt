import Link from "next/link";
import { Claim } from "@/types";
import ClaimStatusBadge from "./ClaimStatusBadge";

export default function ClaimCard({ claim }: { claim: Claim }) {
  return (
    <Link
      href={`/dashboard/claims/${claim.id}`}
      className="block bg-white border border-slate-200 rounded-xl p-5 hover:shadow-md hover:border-slate-300 transition"
    >
      <div className="flex justify-between items-start gap-4">
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-slate-900 truncate">{claim.title}</h3>
          <p className="text-sm text-slate-500 mt-1 line-clamp-2">{claim.description}</p>
          <p className="text-xs text-slate-400 mt-2">
            {new Date(claim.createdAt).toLocaleDateString()}
          </p>
        </div>
        <ClaimStatusBadge status={claim.status} />
      </div>
    </Link>
  );
}