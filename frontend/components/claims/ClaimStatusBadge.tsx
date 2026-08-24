import clsx from "clsx";
import { ClaimStatus } from "@/types";

const statusStyles: Record<ClaimStatus, string> = {
  DRAFT: "bg-slate-100 text-slate-700",
  SUBMITTED: "bg-blue-100 text-blue-700",
  AI_REVIEWING: "bg-indigo-100 text-indigo-700",
  AI_RESOLVED: "bg-green-100 text-green-700",
  CHALLENGED: "bg-amber-100 text-amber-700",
  HUMAN_REVIEW: "bg-purple-100 text-purple-700",
  FINALIZED: "bg-emerald-100 text-emerald-700",
  REJECTED: "bg-red-100 text-red-700",
};

export default function ClaimStatusBadge({ status }: { status: ClaimStatus }) {
  return (
    <span className={clsx("px-2.5 py-1 rounded-full text-xs font-medium", statusStyles[status])}>
      {status.replace("_", " ")}
    </span>
  );
}