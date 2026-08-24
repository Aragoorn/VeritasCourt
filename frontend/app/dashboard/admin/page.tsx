"use client";

import { useEffect, useState } from "react";
import api from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { useRouter } from "next/navigation";
import toast from "react-hot-toast";

export default function AdminPage() {
  const { user } = useAuth();
  const router = useRouter();
  const [stats, setStats] = useState({ totalClaims: 0, pendingReview: 0, users: 0 });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user && user.role !== "SUPER_ADMIN" && user.role !== "COMPANY_ADMIN") {
      toast.error("Access denied");
      router.push("/dashboard");
      return;
    }

    // در نسخه واقعی از endpointهای admin استفاده می‌کنیم
    Promise.all([
      api.get("/claims"),
      api.get("/review/pending"),
    ])
      .then(([claimsRes, reviewRes]) => {
        setStats({
          totalClaims: claimsRes.data.length,
          pendingReview: reviewRes.data.length,
          users: 0, // بعداً endpoint اضافه می‌شود
        });
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [user, router]);

  if (loading) return <p>Loading admin panel...</p>;

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Admin Panel</h1>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white border rounded-xl p-6">
          <p className="text-sm text-slate-500">Total Claims</p>
          <p className="text-3xl font-bold mt-1">{stats.totalClaims}</p>
        </div>
        <div className="bg-white border rounded-xl p-6">
          <p className="text-sm text-slate-500">Pending Human Review</p>
          <p className="text-3xl font-bold mt-1 text-amber-600">{stats.pendingReview}</p>
        </div>
        <div className="bg-white border rounded-xl p-6">
          <p className="text-sm text-slate-500">Users</p>
          <p className="text-3xl font-bold mt-1">{stats.users}</p>
        </div>
      </div>

      <div className="bg-white border rounded-xl p-6">
        <h2 className="font-semibold mb-3">Quick Actions</h2>
        <div className="flex gap-3">
          <button className="px-4 py-2 bg-slate-900 text-white text-sm rounded-lg">
            Manage Companies
          </button>
          <button className="px-4 py-2 bg-slate-100 text-slate-900 text-sm rounded-lg">
            View Audit Logs
          </button>
        </div>
      </div>
    </div>
  );
}