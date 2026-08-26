# Veritas Court v4.0.0
Enterprise Hybrid AI + Human Claim & Dispute Resolution on GenLayer
**Focused Path Tests:** [tests/test_veritas_paths.py](https://github.com/Aragoorn/VeritasCourt/blob/main/tests/test_veritas_paths.py)
**Status:** Production-ready · Addresses full Steward feedback (Aug 2026)  
**Contract Source:** [`https://github.com/Aragoorn/VeritasCourt/blob/main/contracts/VeritasCourt.py`](https://github.com/Aragoorn/VeritasCourt/blob/main/contracts/VeritasCourt.py)  
**Deployed Address:** [`0xb040060c9C0DAb023ecEC11361D05DB1e0D209b0`](https://explorer-studio.genlayer.com/address/0xb040060c9C0DAb023ecEC11361D05DB1e0D209b0)
https://explorer-studio.genlayer.com/address/0xb040060c9C0DAb023ecEC11361D05DB1e0D209b0

---

## Steward Feedback Compliance (v4.0.0)

This release fully implements the steward requests:

1. **Appointed resolver identity + matching endpoint authorization**  
   - Persistent storage: `appointed_resolver`, `appointed_resolver_endpoint`, `resolver_endpoints`, `resolver_authorized`  
   - Functions: `set_appointed_resolver(resolver, endpoint)`, `authorize_resolver(...)`  
   - `_can_resolve()` enforces authorization + minimum resolver stake

2. **Required stake forwarding for challenge & appeal**  
   - Challenge / appeal require and persist `min_challenge_stake` / `min_appeal_stake`  
   - New `min_resolver_stake` enforced on resolve path  
   - Stakes recorded on-chain + `StakeRecorded` events

3. **Human review routed exclusively through `cast_human_vote` + on-chain finalization**  
   - Config flag `require_human_votes_for_finalize` (default `true`)  
   - `finalize_claim` requires sufficient human votes when hybrid mode is active  
   - No off-chain (Prisma-only) finalization path remains

4. **Focused path tests** included (see below)

---

## 1. Project Overview

Veritas Court is a production-ready, enterprise-grade Intelligent Contract built on GenLayer.  
It acts as a transparent, AI-powered first-instance court with optional human hybrid jury support.

It is designed for organizations that need fast, auditable, and challengeable resolution of:

- Commercial disputes  
- Insurance claims  
- Supply-chain issues  
- SaaS / SLA breaches  
- Employment matters  
- IP / Copyright conflicts  
- Other B2B claims

**Current Version:** 4.0.0  
**Status:** Investment-ready and suitable for real organizational deployment.

---

## 2. Core Features

### 2.1 Claim Management
- Full multi-party support (Plaintiff + Defendant + observers)
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
- Hybrid mode: AI recommendation + human resolver votes via `cast_human_vote`
- Minimum credibility threshold enforcement
- Complete on-chain decision history

### 2.4 Challenge & Appeal System
- Stake-based challenges with time-limited windows
- Full second-instance Appeal layer
- Automatic stake recording, management and withdrawal after finalization
- Required stake forwarding enforced on-chain

### 2.5 Finalization & Escrow
- Time-locked challenge / appeal windows
- On-chain-only finalization (`finalize_claim`)
- Built-in escrow locked at claim creation
- Automatic payout based on final decision + protocol fee
- Cross-contract callback support

### 2.6 Access Control & Governance
- Roles: Owner, Admin, Resolver, Senior Resolver
- **Appointed Resolver** with persistent identity + endpoint authorization
- Two-step ownership transfer
- Pause / Unpause
- On-chain reputation system
- Resolver staking (`stake_as_resolver` + `min_resolver_stake`)

### 2.7 Enterprise & Compliance Features
- Configurable jurisdiction and legal disclaimer
- Full audit-trail export (`get_audit_trail`)
- Comprehensive events for external monitoring
- Extensible template system
- Versioned design (currently 4.2.0)

---

## 3. How It Works – Complete Workflow

1. **Claim Creation**  
   User/system creates a claim with parties, evidence, optional escrow, template and jurisdiction.

2. **Evidence Collection**  
   Parties can add more evidence while the claim is open / challenged / appealed.

3. **Resolution**  
   An authorized & staked Resolver calls `resolve_claim`.  
   Contract fetches & scores evidence, runs AI adjudicator, and incorporates human votes (if any).

4. **Challenge Period**  
   Within the time window, parties can challenge by posting the required stake.

5. **Appeal (Optional)**  
   Formal appeal can be submitted with the required stake.

6. **Human Review (Hybrid)**  
   Resolvers cast votes exclusively via `cast_human_vote`.

7. **Finalization (On-chain only)**  
   After windows close, `finalize_claim` is called.  
   When `require_human_votes_for_finalize = true`, sufficient human votes are mandatory.  
   Escrow is released and the claim becomes final.

8. **Archiving**  
   Admins can archive old finalized claims.

---

## 4. Focused Path Tests (against VeritasCourt.py)

These tests demonstrate that every path requested by the steward completes successfully.

### 1. Appointed Resolver + Endpoint Authorization
- Deploy contract
- Call `set_appointed_resolver(resolver_address, "https://your-endpoint.example.com")`
- `get_appointed_resolver()` returns correct identity + endpoint
- `is_authorized_resolver(resolver_address) == true`
- Unauthorized address cannot call `resolve_claim`

### 2. Challenge Stake Forwarding
- `create_claim` → `resolve_claim`
- `challenge` with value ≥ `min_challenge_stake`
- Stake is persisted in `challenge_stakes`
- `StakeRecorded` event is emitted

### 3. Appeal Stake Forwarding
- Same flow as challenge for the appeal path

### 4. Human Vote + On-chain Finalization
- `create_claim` (hybrid mode enabled)
- `resolve_claim`
- `cast_human_vote("VALID")`
- After challenge window → `finalize_claim` succeeds and returns `{"success": true, "on_chain": true}`
- Without enough votes → reverts (when `require_human_votes_for_finalize = true`)

### 5. Resolver Stake Required
- `add_resolver(non-owner)`
- Attempt `resolve_claim` without stake → fails
- `stake_as_resolver` (≥ `min_resolver_stake`) → `resolve_claim` succeeds

---

## 5. How to Test in GenLayer Studio (Step-by-step)

1. Open [GenLayer Studio](https://studio.genlayer.com)
2. Create a new project or open an existing one
3. Paste the full `VeritasCourt.py` (v4.2.0) and **Deploy**
4. Execute the following calls in order:

| Step | Function                    | Notes / Parameters                                      |
|------|-----------------------------|---------------------------------------------------------|
| 1    | `set_appointed_resolver`    | Your address + a valid HTTPS endpoint                   |
| 2    | `stake_as_resolver`         | Send value ≥ `min_resolver_stake` (default 1 GEN)       |
| 3    | `create_claim`              | Fill required fields + at least one valid evidence URL  |
| 4    | `resolve_claim`             | Use the returned `claim_id`                             |
| 5    | `cast_human_vote`           | `claim_id` + `"VALID"` (or INVALID / PARTIALLY_VALID)   |
| 6    | `challenge`                 | `claim_id` + reason + value ≥ `min_challenge_stake`     |
| 7    | Wait for challenge window   | Or advance time in Studio if available                  |
| 8    | `finalize_claim`            | Must succeed and return `on_chain: true`                |

5. After each step, verify with view functions:
   - `get_appointed_resolver`
   - `get_config`
   - `get_claim`
   - `get_human_votes`
   - `get_resolution`
   - `is_authorized_resolver`

---

## 6. Security Model

- All critical write functions protected by role-based access control
- Contract can be paused instantly by admins
- Only HTTPS URLs accepted for evidence
- Mandatory stakes for challenges, appeals and resolvers
- Two-step ownership transfer
- Rate limiting against spam
- AI decisions always accompanied by a clear legal disclaimer
- Full on-chain evidence and decision history (auditable)
- Human finalization path is strictly on-chain

---

## 7. Roles & Permissions Summary

| Role                | Key Permissions                                              |
|---------------------|--------------------------------------------------------------|
| Owner               | Full control + admin management                              |
| Admin               | Pause, configuration, add/authorize resolvers, archive       |
| Appointed Resolver  | Primary resolver identity + endpoint authorization           |
| Resolver            | Resolve claims + cast human votes (must be authorized + staked) |
| Senior Resolver     | Handle appeals                                               |
| Plaintiff / Defendant | Create claims, add evidence, challenge, appeal             |

---

## 8. Technical Notes

- Built with GenLayer equivalence principles (`strict_eq` + `prompt_non_comparative`)
- Deterministic timestamps via transaction context
- All important state changes emit events
- Storage organized for clarity and future extensibility
- Versioned design (current: **4.0.0**)
- Fully compliant with steward requirements for appointed resolver, stake forwarding, and on-chain human finalization

---

## 9. Future-Proof Design

- Modular template system for new industry packs
- Reputation + staking systems for long-term incentive alignment
- Callback hooks for enterprise system integration
- Clear separation of first-instance and appeal layers
- Hybrid human + AI approach remains adaptable as AI capabilities improve

---

**Ready for production use and further roadmap development.**
