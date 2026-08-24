"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import api from "@/lib/api";
import toast from "react-hot-toast";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Textarea } from "@/components/ui/Textarea";

export default function CreateClaimForm() {
  const router = useRouter();
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [evidenceUrls, setEvidenceUrls] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await api.post("/claims", { title, description, evidenceUrls });
      toast.success("Claim created successfully");
      router.push(`/dashboard/claims/${res.data.id}`);
    } catch (err: any) {
      toast.error(err?.response?.data?.message || "Failed to create claim");
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      <Input
        label="Title"
        required
        minLength={5}
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        placeholder="Enter claim title"
      />
      <Textarea
        label="Description"
        required
        minLength={20}
        rows={5}
        value={description}
        onChange={(e) => setDescription(e.target.value)}
        placeholder="Describe the claim in detail..."
      />
      <Input
        label="Evidence URLs (comma separated)"
        value={evidenceUrls}
        onChange={(e) => setEvidenceUrls(e.target.value)}
        placeholder="https://example.com/doc1.pdf, https://..."
      />
      <Button type="submit" disabled={loading} className="w-full">
        {loading ? "Creating..." : "Create Claim"}
      </Button>
    </form>
  );
}