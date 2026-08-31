# Veritas Court v4.4.1
Enterprise Hybrid AI + Human Claim & Dispute Resolution on GenLayer


**Contract Address:** [0xC3A6e79d9E6C828EE7f9A535679720593c9fb4C5](https://explorer-studio.genlayer.com/address/0xC3A6e79d9E6C828EE7f9A535679720593c9fb4C5)


---

## 1. Project Overview

Veritas Court is a production-ready, enterprise-grade Intelligent Contract built on GenLayer.  
It functions as a transparent, AI-powered first-instance court with mandatory hybrid human jury support when enabled.

Designed for organizations that need fast, auditable, and challengeable resolution of commercial disputes, insurance claims, supply-chain issues, SaaS SLA breaches, employment matters, IP conflicts, and other B2B claims.

**Current Version:** 4.4.1  
**Status:** Investment-ready and suitable for real organizational deployment.

---

## 2. Core Features

### 2.1 Claim Management
- Full multi-party support (Plaintiff + Defendant)
- External ID for ERP / CRM integration
- Pre-built industry templates (General, Insurance, Supply Chain, SaaS SLA, Employment, IP)
- Rate limiting to prevent spam
- Archiving of finalized claims

### 2.2 Evidence Handling
- Up to 6 evidence URLs
- Strict HTTPS-only validation
- Advanced credibility scoring + oracle whitelist bonuses
- Evidence hashing for integrity
- Ability to add additional evidence before finalization

### 2.3 AI Adjudication + Hybrid Jury
- GenLayer `prompt_non_comparative` for consensus-safe AI decisions
- Structured JSON output (`decision`, `confidence`, `reasoning`)
- Hybrid mode: AI recommendation + human votes via `cast_human_vote`
- Minimum credibility threshold enforcement
- Complete on-chain decision history

### 2.4 Challenge & Appeal System
- Stake-based challenges with time-limited windows
- Full second-instance Appeal layer
- Stake recording and event emission on-chain
- Required non-zero stake forwarding enforced

### 2.5 Finalization & Escrow
- Time-locked challenge / appeal windows
- Strictly on-chain finalization (`finalize_claim`)
- Escrow amounts are recorded at claim creation
- Escrow and stake settlement can be handled post-finalization
- Cross-contract callback support

### 2.6 Access Control & Governance
- Roles: Owner, Admin, Resolver, Senior Resolver, Appointed Resolver
- Persistent Appointed Resolver with mandatory endpoint authorization
- Two-step ownership transfer
- Pause / Unpause
- On-chain reputation system
- Resolver staking (`stake_as_resolver` + `min_resolver_stake`)

### 2.7 Enterprise & Compliance Features
- Configurable jurisdiction and legal disclaimer
- Full audit-trail export (`get_audit_trail`)
- Comprehensive events for external monitoring
- Extensible template system
- Versioned design (currently 4.4.0)

---

## 3. How It Works – Complete Workflow

1. **Claim Creation** – Create claim with parties, evidence, optional escrow, template and jurisdiction.  
2. **Evidence Collection** – Parties can add more evidence while the claim is open / challenged / appealed.  
3. **Resolution** – Authorized & staked Resolver calls `resolve_claim`. Contract scores evidence and runs AI adjudicator.  
4. **Challenge Period** – Parties can challenge by posting the required non-zero stake.  
5. **Appeal (Optional)** – Formal appeal with required non-zero stake.  
6. **Human Review (Hybrid)** – Resolvers cast votes exclusively via `cast_human_vote`.  
7. **Finalization (On-chain only)** – After windows close, `finalize_claim` is called. Human votes are mandatory when required.  
8. **Archiving** – Admins can archive old finalized claims.

---

## 4. Security Model

- Role-based access control on all critical functions
- Contract can be paused by admins
- Only HTTPS evidence URLs accepted
- Mandatory non-zero stakes for challenge, appeal and resolvers
- Two-step ownership transfer
- Rate limiting
- Clear legal disclaimer on every decision
- Full on-chain audit trail
- Human finalization path is strictly on-chain

---

## 5. Roles & Permissions

| Role                  | Key Permissions                                      |
|-----------------------|------------------------------------------------------|
| Owner                 | Full control + admin management                      |
| Admin                 | Pause, config, add/authorize resolvers, archive      |
| Appointed Resolver    | Primary persistent identity + endpoint authorization |
| Resolver              | Resolve claims + cast human votes (authorized + staked) |
| Senior Resolver       | Handle appeals                                       |
| Plaintiff / Defendant | Create claims, add evidence, challenge, appeal       |

---

## 6. Technical Notes

- Built with GenLayer equivalence principles (`strict_eq` + `prompt_non_comparative`)
- Deterministic timestamps
- All important state changes emit events (with safe emission guards)
- Storage organized for clarity and extensibility
- Version: **4.4.1**
- Fully compliant with steward requirements

---

## 7. Future-Proof Design

- Modular template system
- Reputation + staking for long-term alignment
- Callback hooks for enterprise integration
- Clear first-instance vs appeal separation
- Hybrid AI + Human approach ready for future AI improvements
