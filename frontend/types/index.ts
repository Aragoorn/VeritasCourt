export type UserRole =
  | "SUPER_ADMIN"
  | "COMPANY_ADMIN"
  | "COMPANY_USER"
  | "HUMAN_REVIEWER"
  | "CLAIMANT";

export type ClaimStatus =
  | "DRAFT"
  | "SUBMITTED"
  | "AI_REVIEWING"
  | "AI_RESOLVED"
  | "CHALLENGED"
  | "APPEALED"
  | "HUMAN_REVIEW"
  | "FINALIZED"
  | "REJECTED"
  | "ARCHIVED";

export interface User {
  id: string;
  email: string;
  name?: string;
  role: UserRole;
  companyId?: string;
}

export interface Claim {
  id: string;
  externalId?: string;
  title: string;
  description: string;
  status: ClaimStatus;
  genlayerClaimId?: string;
  companyId: string;
  creatorId: string;
  createdAt: string;
  updatedAt: string;
  evidence?: Evidence[];
  aiResolution?: AiResolution;
  creator?: {
    id: string;
    name?: string;
    email: string;
  };
}

export interface Evidence {
  id: string;
  claimId: string;
  url: string;
  fileName?: string;
  mimeType?: string;
  ipfsHash?: string;
  createdAt: string;
}

export interface AiResolution {
  id: string;
  claimId: string;
  decision: "VALID" | "PARTIALLY_VALID" | "INVALID";
  confidence: number;
  reasoning?: string;
  isReassessment: boolean;
  createdAt: string;
}