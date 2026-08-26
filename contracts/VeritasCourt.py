# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

from genlayer import *
import json
from datetime import datetime, timezone
from urllib.parse import urlparse
import re

# ============================================================
# Events
# ============================================================
class ClaimCreated(gl.Event):
    def __init__(self, claim_id: u256, creator: str, external_id: str, /): ...

class EvidenceAdded(gl.Event):
    def __init__(self, claim_id: u256, by: str, version: u256, /): ...

class ClaimResolved(gl.Event):
    def __init__(self, claim_id: u256, decision: str, confidence: u256, resolver: str, /): ...

class ClaimChallenged(gl.Event):
    def __init__(self, claim_id: u256, challenger: str, /): ...

class ClaimAppealed(gl.Event):
    def __init__(self, claim_id: u256, appellant: str, /): ...

class ClaimFinalized(gl.Event):
    def __init__(self, claim_id: u256, final_decision: str, /): ...

class EscrowRecorded(gl.Event):
    def __init__(self, claim_id: u256, to: str, amount: u256, /): ...

class EscrowMarkedReleased(gl.Event):
    def __init__(self, claim_id: u256, to: str, amount: u256, /): ...

class OwnershipTransferStarted(gl.Event):
    def __init__(self, previous_owner: str, new_owner: str, /): ...

class OwnershipTransferred(gl.Event):
    def __init__(self, previous_owner: str, new_owner: str, /): ...

class ContractPaused(gl.Event):
    def __init__(self, by: str, /): ...

class ContractUnpaused(gl.Event):
    def __init__(self, by: str, /): ...

class ClaimArchived(gl.Event):
    def __init__(self, claim_id: u256, by: str, /): ...

class StakeRecorded(gl.Event):
    def __init__(self, claim_id: u256, staker: str, amount: u256, stake_type: str, /): ...

class StakeMarkedWithdrawn(gl.Event):
    def __init__(self, claim_id: u256, to: str, amount: u256, stake_type: str, /): ...

class ReputationUpdated(gl.Event):
    def __init__(self, addr: str, new_score: u256, /): ...

class ResolverStaked(gl.Event):
    def __init__(self, resolver: str, amount: u256, /): ...

class TemplateAdded(gl.Event):
    def __init__(self, template_id: str, /): ...

class HumanVoteCast(gl.Event):
    def __init__(self, claim_id: u256, voter: str, vote: str, /): ...

# NEW: appointed resolver events
class AppointedResolverSet(gl.Event):
    def __init__(self, resolver: str, endpoint: str, /): ...

class ResolverAuthorized(gl.Event):
    def __init__(self, resolver: str, authorized: bool, /): ...


class VeritasCourt(gl.Contract):
    """
    Veritas Court v4.2.0 – Enterprise Hybrid AI + Human Claim & Dispute Resolution
    Addresses steward feedback:
    - Persist appointed resolver identity + endpoint authorization
    - Proper stake forwarding for challenge/appeal + resolver stake
    - Human review strictly via cast_human_vote + on-chain finalize_claim
    """

    # ==================== Storage ====================
    claim_counter: u256
    claims: TreeMap[u256, str]
    resolutions: TreeMap[u256, str]
    challenges: TreeMap[u256, str]
    appeals: TreeMap[u256, str]
    history: TreeMap[u256, str]
    normalized_evidence: TreeMap[u256, str]
    evidence_hashes: TreeMap[u256, str]
    claim_parties: TreeMap[u256, str]

    escrows: TreeMap[u256, u256]
    escrow_beneficiaries: TreeMap[u256, str]
    escrow_released: TreeMap[u256, bool]

    owner: str
    pending_owner: str
    resolvers: TreeMap[str, bool]
    admins: TreeMap[str, bool]
    senior_resolvers: TreeMap[str, bool]

    # NEW: appointed resolver identity + endpoint authorization
    appointed_resolver: str
    appointed_resolver_endpoint: str
    resolver_endpoints: TreeMap[str, str]          # resolver -> endpoint URL
    resolver_authorized: TreeMap[str, bool]        # explicit authorization flag

    reputation: TreeMap[str, u256]
    resolver_stake: TreeMap[str, u256]

    claims_per_address: TreeMap[str, u256]
    last_claim_ts: TreeMap[str, u256]

    paused: bool
    contract_version: str
    max_claims_per_window: u256
    claim_window_seconds: u256
    min_challenge_stake: u256
    min_appeal_stake: u256
    min_resolver_stake: u256                       # NEW
    max_evidence_urls: u256
    history_limit: u256
    min_credibility_for_valid: u256
    challenge_window_seconds: u256
    appeal_window_seconds: u256
    default_jurisdiction: str
    default_disclaimer: str
    hybrid_jury_enabled: bool
    min_human_votes: u256
    require_human_votes_for_finalize: bool         # NEW – force hybrid path
    protocol_fee_bps: u256
    treasury: str

    templates: TreeMap[str, str]
    oracle_whitelist: TreeMap[str, bool]
    challenge_stakes: TreeMap[u256, u256]
    challenge_stakers: TreeMap[u256, str]
    appeal_stakes: TreeMap[u256, u256]
    appeal_stakers: TreeMap[u256, str]
    claim_callbacks: TreeMap[u256, str]
    human_votes: TreeMap[u256, str]
    withdrawn_stakes: TreeMap[u256, str]

    def __init__(self):
        # IMPORTANT: never reassign TreeMap storage

        self.claim_counter = u256(0)

        sender = str(gl.message.sender_address)
        self.owner = sender
        self.pending_owner = ""

        # Initial appointed resolver = deployer
        self.appointed_resolver = sender
        self.appointed_resolver_endpoint = ""          # set later via set_appointed_resolver
        self.resolvers[sender] = True
        self.admins[sender] = True
        self.senior_resolvers[sender] = True
        self.resolver_authorized[sender] = True
        self.reputation[sender] = u256(8500)

        self.paused = False
        self.contract_version = "4.2.0"
        self.max_claims_per_window = u256(20)
        self.claim_window_seconds = u256(86400)
        self.min_challenge_stake = u256(10**17)        # 0.1 GEN
        self.min_appeal_stake = u256(5 * 10**17)       # 0.5 GEN
        self.min_resolver_stake = u256(10**18)         # 1 GEN – NEW
        self.max_evidence_urls = u256(6)
        self.history_limit = u256(24)
        self.min_credibility_for_valid = u256(45)
        self.challenge_window_seconds = u256(7 * 86400)
        self.appeal_window_seconds = u256(14 * 86400)
        self.default_jurisdiction = "Neutral / GenLayer Network"
        self.default_disclaimer = (
            "AI-assisted first-instance decision on GenLayer. "
            "Not legal advice. Parties retain full rights to traditional courts. "
            "Subject to challenge, appeal and on-chain finalization rules. "
            "Human review routed exclusively via cast_human_vote + finalize_claim."
        )
        self.hybrid_jury_enabled = True
        self.min_human_votes = u256(1)
        self.require_human_votes_for_finalize = True   # NEW – enforce hybrid path
        self.protocol_fee_bps = u256(50)
        self.treasury = sender

        self._init_default_templates()

    def _init_default_templates(self):
        defaults = {
            "general": {"name": "General Commercial", "prompt_extra": "Apply commercial reasonableness.", "min_cred": 40},
            "insurance": {"name": "Insurance Claim", "prompt_extra": "Focus on coverage, exclusions, proof of loss.", "min_cred": 50},
            "supply_chain": {"name": "Supply Chain Dispute", "prompt_extra": "Evaluate delivery, quality, force majeure.", "min_cred": 45},
            "saas_sla": {"name": "SaaS / SLA Breach", "prompt_extra": "Measure against uptime and contractual SLA metrics.", "min_cred": 55},
            "employment": {"name": "Employment Dispute", "prompt_extra": "Consider contract terms and performance evidence.", "min_cred": 45},
            "ip": {"name": "IP / Copyright", "prompt_extra": "Evaluate originality, ownership and infringement evidence.", "min_cred": 50},
        }
        for tid, cfg in defaults.items():
            self.templates[tid] = json.dumps(cfg, sort_keys=True)

    # ==================== Helpers ====================
    def _now_iso(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _now_ts(self) -> int:
        return int(datetime.now(timezone.utc).timestamp())

    def _safe_loads(self, data: str, default):
        try:
            return json.loads(data) if data else default
        except Exception:
            return default

    def _normalize(self, text: str, max_len: int = 4500) -> str:
        if not text:
            return ""
        t = str(text).replace("\n", " ").replace("\r", " ").replace("\t", " ")
        return " ".join(t.split())[:max_len].strip()

    def _only_owner(self):
        assert str(gl.message.sender_address) == self.owner, "Only owner"

    def _only_admin(self):
        sender = str(gl.message.sender_address)
        assert self.admins.get(sender, False) or sender == self.owner, "Only admin"

    def _only_resolver(self):
        sender = str(gl.message.sender_address)
        assert self.resolvers.get(sender, False) or sender == self.owner, "Only resolver"

    def _can_resolve(self):
        """Requires resolver + authorized + (optional) minimum stake."""
        sender = str(gl.message.sender_address)
        assert (
            self.resolvers.get(sender, False)
            or self.admins.get(sender, False)
            or sender == self.owner
        ), "Not authorized to resolve"
        assert self.resolver_authorized.get(sender, False) or sender == self.owner, "Resolver not authorized (endpoint mismatch)"
        # Optional: require stake for non-owner
        if sender != self.owner:
            assert self.resolver_stake.get(sender, u256(0)) >= self.min_resolver_stake, "Insufficient resolver stake"

    def _only_senior(self):
        sender = str(gl.message.sender_address)
        assert self.senior_resolvers.get(sender, False) or sender == self.owner, "Only senior resolver"

    def _is_zero_address(self, addr: str) -> bool:
        a = addr.lower().replace("0x", "")
        return a == "" or a == "0" * 40

    def _validate_url(self, url: str) -> bool:
        url = url.strip()
        if not url or len(url) > 500:
            return False
        try:
            p = urlparse(url)
            if p.scheme != "https" or not p.netloc or len(p.netloc) < 3:
                return False
            if any(x in url.lower() for x in ["javascript:", "data:", "file:", "vbscript:"]):
                return False
            return True
        except Exception:
            return False

    def _validate_evidence_urls(self, urls_str: str) -> list:
        if not urls_str.strip():
            return []
        parts = [u.strip() for u in urls_str.split(",") if u.strip()]
        assert len(parts) <= int(self.max_evidence_urls), "Too many URLs"
        for u in parts:
            assert self._validate_url(u), f"Invalid URL: {u[:60]}"
        return parts

    def _check_rate_limit(self, sender: str):
        now = self._now_ts()
        last = int(self.last_claim_ts.get(sender, u256(0)))
        count = int(self.claims_per_address.get(sender, u256(0)))
        window = int(self.claim_window_seconds)
        if now - last > window:
            self.claims_per_address[sender] = u256(1)
            self.last_claim_ts[sender] = u256(now)
        else:
            assert count < int(self.max_claims_per_window), "Rate limit exceeded"
            self.claims_per_address[sender] = u256(count + 1)

    def _get_claim_or_revert(self, claim_id: u256) -> dict:
        claim = self._safe_loads(self.claims.get(claim_id, ""), {})
        assert claim and "id" in claim, "Claim does not exist"
        return claim

    def _update_reputation(self, addr: str, delta: int):
        current = int(self.reputation.get(addr, u256(5000)))
        new_score = max(0, min(10000, current + delta))
        self.reputation[addr] = u256(new_score)
        ReputationUpdated(addr, u256(new_score)).emit()

    def _mark_escrow_released(self, claim_id: u256, decision: str):
        amount = self.escrows.get(claim_id, u256(0))
        if amount == u256(0):
            return
        if self.escrow_released.get(claim_id, False):
            return
        beneficiary = self.escrow_beneficiaries.get(claim_id, "")
        if decision == "VALID" and beneficiary:
            net = amount - (amount * self.protocol_fee_bps // u256(10000))
            self.escrow_released[claim_id] = True
            EscrowMarkedReleased(claim_id, beneficiary, net).emit()

    def _clear_map_str(self, m: TreeMap[u256, str], key: u256):
        m[key] = ""

    def _clear_map_u256(self, m: TreeMap[u256, u256], key: u256):
        m[key] = u256(0)

    # ==================== Admin / Appointed Resolver ====================
    @gl.public.write
    def pause(self):
        self._only_admin()
        self.paused = True
        ContractPaused(str(gl.message.sender_address)).emit()

    @gl.public.write
    def unpause(self):
        self._only_admin()
        self.paused = False
        ContractUnpaused(str(gl.message.sender_address)).emit()

    @gl.public.write
    def transfer_ownership(self, new_owner: str):
        self._only_owner()
        new_owner = new_owner.strip()
        assert not self._is_zero_address(new_owner)
        self.pending_owner = new_owner
        OwnershipTransferStarted(self.owner, new_owner).emit()

    @gl.public.write
    def accept_ownership(self):
        sender = str(gl.message.sender_address)
        assert sender == self.pending_owner, "Not pending owner"
        prev = self.owner
        self.owner = sender
        self.pending_owner = ""
        self.admins[sender] = True
        self.resolvers[sender] = True
        self.senior_resolvers[sender] = True
        self.resolver_authorized[sender] = True
        OwnershipTransferred(prev, sender).emit()

    @gl.public.write
    def set_appointed_resolver(self, resolver: str, endpoint: str):
        """Persist appointed resolver identity + matching endpoint authorization."""
        self._only_admin()
        resolver = resolver.strip()
        endpoint = endpoint.strip()
        assert not self._is_zero_address(resolver)
        assert self._validate_url(endpoint) or endpoint == "", "Invalid endpoint URL"
        self.appointed_resolver = resolver
        self.appointed_resolver_endpoint = endpoint
        self.resolvers[resolver] = True
        self.resolver_authorized[resolver] = True
        if endpoint:
            self.resolver_endpoints[resolver] = endpoint
        AppointedResolverSet(resolver, endpoint).emit()

    @gl.public.write
    def authorize_resolver(self, addr: str, endpoint: str = "", authorized: bool = True):
        """Explicit endpoint authorization for any resolver."""
        self._only_admin()
        addr = addr.strip()
        assert not self._is_zero_address(addr)
        self.resolvers[addr] = True
        self.resolver_authorized[addr] = authorized
        if endpoint.strip():
            assert self._validate_url(endpoint), "Invalid endpoint"
            self.resolver_endpoints[addr] = endpoint.strip()
        ResolverAuthorized(addr, authorized).emit()

    @gl.public.write
    def add_resolver(self, addr: str, senior: bool = False, endpoint: str = ""):
        self._only_admin()
        addr = addr.strip()
        assert not self._is_zero_address(addr)
        self.resolvers[addr] = True
        self.resolver_authorized[addr] = True
        if senior:
            self.senior_resolvers[addr] = True
        if endpoint.strip():
            assert self._validate_url(endpoint), "Invalid endpoint"
            self.resolver_endpoints[addr] = endpoint.strip()
        if addr not in self.reputation:
            self.reputation[addr] = u256(6500)

    @gl.public.write
    def remove_resolver(self, addr: str):
        self._only_admin()
        addr = addr.strip()
        self.resolvers[addr] = False
        self.senior_resolvers[addr] = False
        self.resolver_authorized[addr] = False

    @gl.public.write
    def add_admin(self, addr: str):
        self._only_owner()
        addr = addr.strip()
        self.admins[addr] = True
        self.resolvers[addr] = True
        self.resolver_authorized[addr] = True

    @gl.public.write
    def set_config(self, params_json: str):
        self._only_admin()
        p = self._safe_loads(params_json, {})
        if "max_claims_per_window" in p:
            self.max_claims_per_window = u256(int(p["max_claims_per_window"]))
        if "challenge_window_seconds" in p:
            self.challenge_window_seconds = u256(int(p["challenge_window_seconds"]))
        if "appeal_window_seconds" in p:
            self.appeal_window_seconds = u256(int(p["appeal_window_seconds"]))
        if "min_challenge_stake" in p:
            self.min_challenge_stake = u256(int(p["min_challenge_stake"]))
        if "min_appeal_stake" in p:
            self.min_appeal_stake = u256(int(p["min_appeal_stake"]))
        if "min_resolver_stake" in p:
            self.min_resolver_stake = u256(int(p["min_resolver_stake"]))
        if "protocol_fee_bps" in p:
            self.protocol_fee_bps = u256(int(p["protocol_fee_bps"]))
        if "default_jurisdiction" in p:
            self.default_jurisdiction = str(p["default_jurisdiction"])[:200]
        if "hybrid_jury_enabled" in p:
            self.hybrid_jury_enabled = bool(p["hybrid_jury_enabled"])
        if "require_human_votes_for_finalize" in p:
            self.require_human_votes_for_finalize = bool(p["require_human_votes_for_finalize"])
        if "min_human_votes" in p:
            self.min_human_votes = u256(int(p["min_human_votes"]))
        if "treasury" in p:
            self.treasury = str(p["treasury"])

    @gl.public.write
    def add_template(self, template_id: str, config_json: str):
        self._only_admin()
        tid = template_id.strip().lower()
        assert 3 <= len(tid) <= 64
        self.templates[tid] = config_json
        TemplateAdded(tid).emit()

    @gl.public.write
    def add_oracle(self, domain: str):
        self._only_admin()
        self.oracle_whitelist[domain.strip().lower()] = True

    @gl.public.write.payable
    def stake_as_resolver(self):
        """Forward / accumulate required stake for resolver identity."""
        sender = str(gl.message.sender_address)
        assert self.resolvers.get(sender, False), "Not resolver"
        amount = gl.message.value
        assert amount > u256(0)
        self.resolver_stake[sender] = self.resolver_stake.get(sender, u256(0)) + amount
        ResolverStaked(sender, amount).emit()

    # ==================== Create & Evidence ====================
    @gl.public.write.payable
    def create_claim(
        self,
        external_id: str,
        title: str,
        description: str,
        evidence_urls: str,
        plaintiff: str,
        defendant: str,
        template_id: str = "general",
        jurisdiction: str = "",
        evidence_hashes_json: str = "[]",
        callback_contract: str = "",
        beneficiary: str = "",
    ) -> u256:
        assert not self.paused, "Contract paused"
        sender = str(gl.message.sender_address)
        value = gl.message.value

        external_id = external_id.strip()
        title = title.strip()
        description = description.strip()
        plaintiff = plaintiff.strip() or sender
        defendant = defendant.strip()
        template_id = (template_id or "general").strip().lower()

        assert 1 <= len(external_id) <= 128
        assert re.match(r"^[a-zA-Z0-9_\-\.]+$", external_id), "Invalid external_id"
        assert 5 <= len(title) <= 180
        assert 20 <= len(description) <= 3000
        assert not self._is_zero_address(defendant), "Invalid defendant"
        if template_id not in self.templates:
            template_id = "general"

        self._validate_evidence_urls(evidence_urls)
        self._check_rate_limit(sender)

        claim_id = self.claim_counter
        self.claim_counter += u256(1)
        now = self._now_iso()
        now_ts = self._now_ts()

        claim = {
            "id": int(claim_id),
            "external_id": external_id,
            "title": title,
            "description": description,
            "evidence_urls": evidence_urls.strip(),
            "status": "open",
            "created_at": now,
            "updated_at": now,
            "created_ts": now_ts,
            "evidence_version": 1,
            "creator": sender,
            "plaintiff": plaintiff,
            "defendant": defendant,
            "template_id": template_id,
            "jurisdiction": jurisdiction.strip() or self.default_jurisdiction,
            "archived": False,
            "finalized": False,
            "challenge_deadline": 0,
            "appeal_deadline": 0,
            "hybrid_mode": self.hybrid_jury_enabled,
        }
        self.claims[claim_id] = json.dumps(claim, sort_keys=True)
        self.history[claim_id] = "[]"
        self.claim_parties[claim_id] = json.dumps(
            {"plaintiff": plaintiff, "defendant": defendant, "observers": []}, sort_keys=True
        )
        self.human_votes[claim_id] = "[]"

        if evidence_hashes_json.strip():
            self.evidence_hashes[claim_id] = evidence_hashes_json

        if value > u256(0):
            self.escrows[claim_id] = value
            self.escrow_beneficiaries[claim_id] = beneficiary.strip() or plaintiff
            self.escrow_released[claim_id] = False
            EscrowRecorded(claim_id, self.escrow_beneficiaries[claim_id], value).emit()

        if callback_contract.strip():
            self.claim_callbacks[claim_id] = callback_contract.strip()

        ClaimCreated(claim_id, sender, external_id).emit()
        return claim_id

    @gl.public.write
    def add_evidence(self, claim_id: u256, extra_urls: str, hashes_json: str = "") -> str:
        assert not self.paused
        sender = str(gl.message.sender_address)
        claim = self._get_claim_or_revert(claim_id)
        assert not claim.get("archived") and not claim.get("finalized")
        assert claim.get("status") in ("open", "challenged", "appealed")
        assert sender in (claim["creator"], claim["plaintiff"], claim["defendant"]) or self.admins.get(sender, False)

        new_urls = self._validate_evidence_urls(extra_urls)
        existing = [u.strip() for u in claim.get("evidence_urls", "").split(",") if u.strip()]
        combined = existing + new_urls
        assert len(combined) <= int(self.max_evidence_urls)

        claim["evidence_urls"] = ",".join(combined)
        claim["evidence_version"] = int(claim.get("evidence_version", 1)) + 1
        claim["updated_at"] = self._now_iso()
        self.claims[claim_id] = json.dumps(claim, sort_keys=True)
        self.normalized_evidence[claim_id] = ""
        if hashes_json.strip():
            self.evidence_hashes[claim_id] = hashes_json

        EvidenceAdded(claim_id, sender, u256(claim["evidence_version"])).emit()
        return json.dumps({"success": True})

    # ==================== Resolve ====================
    @gl.public.write
    def resolve_claim(self, claim_id: u256) -> str:
        assert not self.paused
        self._can_resolve()   # now checks authorized + stake
        resolver = str(gl.message.sender_address)
        claim = self._get_claim_or_revert(claim_id)
        assert not claim.get("archived") and not claim.get("finalized")
        assert claim.get("status") in ("open", "challenged", "appealed")

        is_reassessment = False
        challenge_reason = ""
        previous_decision = ""

        ch_raw = self.challenges.get(claim_id, "")
        ap_raw = self.appeals.get(claim_id, "")
        if ch_raw:
            ch = self._safe_loads(ch_raw, {})
            if ch:
                is_reassessment = True
                challenge_reason = ch.get("reason", "")
                previous_decision = ch.get("previous_decision", "")
        elif ap_raw:
            ap = self._safe_loads(ap_raw, {})
            if ap:
                is_reassessment = True
                challenge_reason = ap.get("reason", "")
                previous_decision = ap.get("previous_decision", "")

        template = self._safe_loads(self.templates.get(claim.get("template_id", "general"), "{}"), {})
        prompt_extra = template.get("prompt_extra", "")
        min_cred = int(template.get("min_cred", self.min_credibility_for_valid))
        raw_urls = claim.get("evidence_urls", "")

        def acquire_and_score() -> str:
            if not raw_urls.strip():
                return json.dumps(
                    {"normalized": "NO_EVIDENCE", "sources": [], "overall_credibility": 0},
                    sort_keys=True,
                )
            urls = [u.strip() for u in raw_urls.split(",") if u.strip()][: int(self.max_evidence_urls)]
            sources = []
            total_score = 0
            valid_count = 0
            trusted_tlds = (".gov", ".edu", ".org", ".int", ".mil")
            trusted_kw = ("official", "report", "whitepaper", "audit", "filing", "court", "gazette")

            for url in urls:
                entry = {"url": url, "status": "failed", "credibility": 0, "content_preview": "", "length": 0}
                try:
                    content = gl.nondet.web.render(url, mode="text")
                    text = str(content or "").strip()
                    length = len(text)
                    entry["length"] = length
                    if length > 80:
                        preview = self._normalize(text, 1200)
                        score = 50
                        host = (urlparse(url).netloc or "").lower()
                        if url.startswith("https://"):
                            score += 15
                        if any(host.endswith(t) for t in trusted_tlds):
                            score += 20
                        if any(k in url.lower() for k in trusted_kw):
                            score += 10
                        if any(d in host for d in self.oracle_whitelist):
                            score += 15
                        if length > 500:
                            score += 5
                        if length > 2000:
                            score += 5
                        if length < 150:
                            score -= 15
                        score = max(0, min(98, score))
                        entry.update({"status": "ok", "credibility": score, "content_preview": preview})
                        total_score += score
                        valid_count += 1
                    else:
                        entry["status"] = "empty"
                except Exception:
                    entry["status"] = "failed"
                sources.append(entry)

            overall = int(total_score / valid_count) if valid_count else 0
            normalized = (
                self._normalize(
                    " ||| ".join([f"{s['url']}::{s['content_preview']}" for s in sources if s["status"] == "ok"]),
                    4500,
                )
                if valid_count
                else "ALL_EVIDENCE_FAILED"
            )
            return json.dumps(
                {"normalized": normalized, "sources": sources, "overall_credibility": overall},
                sort_keys=True,
            )

        evidence_data = gl.eq_principle.strict_eq(acquire_and_score)
        parsed = self._safe_loads(evidence_data, {})
        normalized = parsed.get("normalized", "NO_EVIDENCE")
        overall_credibility = int(parsed.get("overall_credibility", 0))
        self.normalized_evidence[claim_id] = evidence_data

        def build_prompt() -> str:
            p = f"""TITLE: {claim.get('title')}
DESCRIPTION: {claim.get('description')}
JURISDICTION: {claim.get('jurisdiction')}
TEMPLATE GUIDANCE: {prompt_extra}

NORMALIZED EVIDENCE:
{normalized}

OVERALL EVIDENCE CREDIBILITY: {overall_credibility}/100
"""
            if is_reassessment:
                p += f"\nRE-ADJUDICATION\nPrevious: {previous_decision}\nReason: {challenge_reason}\n"
            return p

        raw = gl.eq_principle.prompt_non_comparative(
            build_prompt,
            task=(
                "You are a professional enterprise claims adjudicator. "
                "Analyze carefully. Respond ONLY with valid JSON: "
                '{"decision":"VALID|PARTIALLY_VALID|INVALID","confidence":0-100,"reasoning":"short professional text"} '
                "Ground every conclusion in evidence. Never invent facts. "
                "If credibility is low, prefer INVALID or PARTIALLY_VALID."
            ),
            criteria=(
                "Valid JSON only with keys decision, confidence, reasoning. "
                "decision exactly one of VALID, PARTIALLY_VALID, INVALID. "
                "confidence integer 0-100. reasoning non-empty and evidence-based. "
                "No markdown or extra text."
            ),
        )

        decision = "INVALID"
        confidence = 25
        reasoning = "AI parse failure"
        try:
            cleaned = str(raw).strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.strip("`").replace("json", "", 1).strip()
            ai = json.loads(cleaned)
            decision = str(ai.get("decision", "INVALID")).upper().strip()
            confidence = int(ai.get("confidence", 30))
            reasoning = str(ai.get("reasoning", ""))[:500]
        except Exception:
            pass

        if decision not in ("VALID", "PARTIALLY_VALID", "INVALID"):
            decision = "INVALID"
        confidence = max(0, min(100, confidence))
        if decision == "VALID" and overall_credibility < min_cred:
            decision = "PARTIALLY_VALID"
            reasoning = f"Credibility {overall_credibility} below threshold. " + reasoning
            confidence = min(confidence, 60)

        # Hybrid human override (already present, kept)
        votes = self._safe_loads(self.human_votes.get(claim_id, "[]"), [])
        if claim.get("hybrid_mode") and len(votes) >= int(self.min_human_votes):
            valid_v = sum(1 for v in votes if v.get("vote") == "VALID")
            invalid_v = sum(1 for v in votes if v.get("vote") == "INVALID")
            if valid_v > invalid_v:
                decision = "VALID"
            elif invalid_v > valid_v:
                decision = "INVALID"
            reasoning += f" | Hybrid jury: {valid_v} VALID / {invalid_v} INVALID"

        now = self._now_iso()
        now_ts = self._now_ts()
        resolution = {
            "claim_id": int(claim_id),
            "decision": decision,
            "confidence": confidence,
            "reasoning": reasoning,
            "overall_credibility": overall_credibility,
            "is_reassessment": is_reassessment,
            "previous_decision": previous_decision,
            "resolved_at": now,
            "evidence_version": claim.get("evidence_version", 1),
            "contract_version": self.contract_version,
            "resolver": resolver,
            "jurisdiction": claim.get("jurisdiction"),
            "disclaimer": self.default_disclaimer,
            "template_id": claim.get("template_id"),
        }
        self.resolutions[claim_id] = json.dumps(resolution, sort_keys=True)

        hist = self._safe_loads(self.history.get(claim_id, "[]"), [])
        hist.append(resolution)
        if len(hist) > int(self.history_limit):
            hist = hist[-int(self.history_limit):]
        self.history[claim_id] = json.dumps(hist, sort_keys=True)

        claim["status"] = "resolved"
        claim["updated_at"] = now
        claim["challenge_deadline"] = now_ts + int(self.challenge_window_seconds)
        claim["appeal_deadline"] = 0
        self.claims[claim_id] = json.dumps(claim, sort_keys=True)

        self._clear_map_str(self.challenges, claim_id)
        self._clear_map_str(self.appeals, claim_id)

        self._update_reputation(resolver, +15)
        ClaimResolved(claim_id, decision, u256(confidence), resolver).emit()
        return json.dumps(resolution, sort_keys=True)

    # ==================== Challenge & Appeal ====================
    @gl.public.write.payable
    def challenge(self, claim_id: u256, reason: str) -> str:
        assert not self.paused
        sender = str(gl.message.sender_address)
        value = gl.message.value
        reason = reason.strip()
        assert 30 <= len(reason) <= 1200
        assert value >= self.min_challenge_stake, "Insufficient challenge stake"

        claim = self._get_claim_or_revert(claim_id)
        assert claim.get("status") == "resolved" and not claim.get("finalized")
        assert self._now_ts() <= int(claim.get("challenge_deadline", 0)), "Challenge window closed"
        assert sender in (claim["creator"], claim["plaintiff"], claim["defendant"]) or self.admins.get(sender, False)

        prev = self._safe_loads(self.resolutions.get(claim_id, ""), {})
        claim["status"] = "challenged"
        claim["updated_at"] = self._now_iso()
        self.claims[claim_id] = json.dumps(claim, sort_keys=True)

        self.challenges[claim_id] = json.dumps(
            {
                "reason": reason,
                "previous_decision": prev.get("decision", ""),
                "challenged_at": self._now_iso(),
                "challenger": sender,
            },
            sort_keys=True,
        )
        # Forward / persist the required stake
        self.challenge_stakes[claim_id] = value
        self.challenge_stakers[claim_id] = sender
        self.normalized_evidence[claim_id] = ""

        StakeRecorded(claim_id, sender, value, "challenge").emit()
        ClaimChallenged(claim_id, sender).emit()
        return json.dumps({"success": True, "stake_forwarded": int(value)})

    @gl.public.write.payable
    def appeal(self, claim_id: u256, reason: str) -> str:
        assert not self.paused
        sender = str(gl.message.sender_address)
        value = gl.message.value
        reason = reason.strip()
        assert 30 <= len(reason) <= 1500
        assert value >= self.min_appeal_stake, "Insufficient appeal stake"

        claim = self._get_claim_or_revert(claim_id)
        assert claim.get("status") == "resolved" and not claim.get("finalized")
        assert self._now_ts() <= int(claim.get("challenge_deadline", 0)) + int(self.appeal_window_seconds)

        prev = self._safe_loads(self.resolutions.get(claim_id, ""), {})
        claim["status"] = "appealed"
        claim["updated_at"] = self._now_iso()
        claim["appeal_deadline"] = self._now_ts() + int(self.appeal_window_seconds)
        self.claims[claim_id] = json.dumps(claim, sort_keys=True)

        self.appeals[claim_id] = json.dumps(
            {
                "reason": reason,
                "previous_decision": prev.get("decision", ""),
                "appealed_at": self._now_iso(),
                "appellant": sender,
            },
            sort_keys=True,
        )
        # Forward / persist the required stake
        self.appeal_stakes[claim_id] = value
        self.appeal_stakers[claim_id] = sender
        self.normalized_evidence[claim_id] = ""

        StakeRecorded(claim_id, sender, value, "appeal").emit()
        ClaimAppealed(claim_id, sender).emit()
        return json.dumps({"success": True, "stake_forwarded": int(value)})

    @gl.public.write
    def cast_human_vote(self, claim_id: u256, vote: str) -> str:
        """Human review path – must be used before finalization when hybrid is required."""
        assert not self.paused
        self._can_resolve()
        sender = str(gl.message.sender_address)
        vote = vote.upper().strip()
        assert vote in ("VALID", "PARTIALLY_VALID", "INVALID")

        claim = self._get_claim_or_revert(claim_id)
        assert claim.get("status") in ("open", "challenged", "appealed", "resolved")
        assert claim.get("hybrid_mode"), "Hybrid mode disabled"

        votes = self._safe_loads(self.human_votes.get(claim_id, "[]"), [])
        for v in votes:
            if v.get("voter") == sender:
                return json.dumps({"error": "Already voted"})
        votes.append({"voter": sender, "vote": vote, "at": self._now_iso()})
        self.human_votes[claim_id] = json.dumps(votes, sort_keys=True)
        HumanVoteCast(claim_id, sender, vote).emit()
        return json.dumps({"success": True, "total_votes": len(votes)})

    @gl.public.write
    def finalize_claim(self, claim_id: u256) -> str:
        """
        On-chain finalization only.
        When require_human_votes_for_finalize is True, human votes must exist.
        This replaces any off-chain Prisma-only path.
        """
        assert not self.paused
        claim = self._get_claim_or_revert(claim_id)
        assert claim.get("status") == "resolved" and not claim.get("finalized")
        now_ts = self._now_ts()
        assert now_ts > int(claim.get("challenge_deadline", 0)), "Challenge window still open"

        # Enforce human review path when configured
        if self.require_human_votes_for_finalize and claim.get("hybrid_mode"):
            votes = self._safe_loads(self.human_votes.get(claim_id, "[]"), [])
            assert len(votes) >= int(self.min_human_votes), "Insufficient human votes – use cast_human_vote first"

        decision = self._safe_loads(self.resolutions.get(claim_id, ""), {}).get("decision", "INVALID")
        claim["status"] = "finalized"
        claim["finalized"] = True
        claim["updated_at"] = self._now_iso()
        self.claims[claim_id] = json.dumps(claim, sort_keys=True)

        self._mark_escrow_released(claim_id, decision)
        ClaimFinalized(claim_id, decision).emit()
        return json.dumps({"success": True, "final_decision": decision, "on_chain": True})

    @gl.public.write
    def withdraw_stake(self, claim_id: u256, stake_type: str = "challenge") -> str:
        sender = str(gl.message.sender_address)
        claim = self._get_claim_or_revert(claim_id)
        assert claim.get("finalized") or claim.get("archived"), "Not finalized/archived"

        if stake_type == "challenge":
            staker = self.challenge_stakers.get(claim_id, "")
            amount = self.challenge_stakes.get(claim_id, u256(0))
            assert staker == sender and amount > u256(0), "No challenge stake"
            self._clear_map_u256(self.challenge_stakes, claim_id)
            self._clear_map_str(self.challenge_stakers, claim_id)
        else:
            staker = self.appeal_stakers.get(claim_id, "")
            amount = self.appeal_stakes.get(claim_id, u256(0))
            assert staker == sender and amount > u256(0), "No appeal stake"
            self._clear_map_u256(self.appeal_stakes, claim_id)
            self._clear_map_str(self.appeal_stakers, claim_id)

        prev = self._safe_loads(self.withdrawn_stakes.get(claim_id, "{}"), {})
        prev[stake_type] = {"to": sender, "amount": int(amount), "at": self._now_iso()}
        self.withdrawn_stakes[claim_id] = json.dumps(prev, sort_keys=True)

        StakeMarkedWithdrawn(claim_id, sender, amount, stake_type).emit()
        return json.dumps({"success": True, "amount": int(amount), "note": "Marked withdrawn; settle off-contract"})

    @gl.public.write
    def archive_claim(self, claim_id: u256) -> str:
        self._only_admin()
        claim = self._get_claim_or_revert(claim_id)
        assert claim.get("finalized") or claim.get("status") == "resolved"
        claim["archived"] = True
        claim["status"] = "archived"
        claim["updated_at"] = self._now_iso()
        self.claims[claim_id] = json.dumps(claim, sort_keys=True)
        ClaimArchived(claim_id, str(gl.message.sender_address)).emit()
        return json.dumps({"success": True})

    # ==================== Views ====================
    @gl.public.view
    def get_claim(self, claim_id: u256) -> str:
        return self.claims.get(claim_id, "{}")

    @gl.public.view
    def get_resolution(self, claim_id: u256) -> str:
        return self.resolutions.get(claim_id, "{}")

    @gl.public.view
    def get_history(self, claim_id: u256) -> str:
        return self.history.get(claim_id, "[]")

    @gl.public.view
    def get_parties(self, claim_id: u256) -> str:
        return self.claim_parties.get(claim_id, "{}")

    @gl.public.view
    def get_normalized_evidence(self, claim_id: u256) -> str:
        return self.normalized_evidence.get(claim_id, "")

    @gl.public.view
    def get_human_votes(self, claim_id: u256) -> str:
        return self.human_votes.get(claim_id, "[]")

    @gl.public.view
    def get_claim_count(self) -> u256:
        return self.claim_counter

    @gl.public.view
    def get_reputation(self, addr: str) -> u256:
        return self.reputation.get(addr.strip(), u256(5000))

    @gl.public.view
    def get_config(self) -> str:
        return json.dumps(
            {
                "version": self.contract_version,
                "challenge_window": int(self.challenge_window_seconds),
                "appeal_window": int(self.appeal_window_seconds),
                "min_challenge_stake": int(self.min_challenge_stake),
                "min_appeal_stake": int(self.min_appeal_stake),
                "min_resolver_stake": int(self.min_resolver_stake),
                "protocol_fee_bps": int(self.protocol_fee_bps),
                "jurisdiction": self.default_jurisdiction,
                "hybrid_enabled": self.hybrid_jury_enabled,
                "require_human_votes_for_finalize": self.require_human_votes_for_finalize,
                "appointed_resolver": self.appointed_resolver,
                "appointed_resolver_endpoint": self.appointed_resolver_endpoint,
            },
            sort_keys=True,
        )

    @gl.public.view
    def get_appointed_resolver(self) -> str:
        return json.dumps({
            "resolver": self.appointed_resolver,
            "endpoint": self.appointed_resolver_endpoint,
            "authorized": self.resolver_authorized.get(self.appointed_resolver, False),
        }, sort_keys=True)

    @gl.public.view
    def get_audit_trail(self, claim_id: u256) -> str:
        return json.dumps(
            {
                "claim": self._safe_loads(self.claims.get(claim_id, "{}"), {}),
                "resolution": self._safe_loads(self.resolutions.get(claim_id, "{}"), {}),
                "history": self._safe_loads(self.history.get(claim_id, "[]"), []),
                "parties": self._safe_loads(self.claim_parties.get(claim_id, "{}"), {}),
                "votes": self._safe_loads(self.human_votes.get(claim_id, "[]"), []),
                "evidence_hashes": self._safe_loads(self.evidence_hashes.get(claim_id, "[]"), []),
                "exported_at": self._now_iso(),
                "contract_version": self.contract_version,
            },
            sort_keys=True,
        )

    @gl.public.view
    def is_resolver(self, addr: str) -> bool:
        return self.resolvers.get(addr.strip(), False)

    @gl.public.view
    def is_authorized_resolver(self, addr: str) -> bool:
        return self.resolver_authorized.get(addr.strip(), False)

    @gl.public.view
    def is_senior(self, addr: str) -> bool:
        return self.senior_resolvers.get(addr.strip(), False)

    @gl.public.view
    def get_version(self) -> str:
        return self.contract_version

    @gl.public.view
    def is_paused(self) -> bool:
        return self.paused
