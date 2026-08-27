# Focused Path Tests – VeritasCourt.py v4.4.0

These tests demonstrate that every path requested by the steward completes successfully under the hardened rules of v4.4.0.

### 1. Appointed Resolver + Endpoint Authorization (Non-Ephemeral)
- [ ] Deploy contract
- [ ] Call `set_appointed_resolver(resolver_address, "https://api.github.com")` (endpoint must be valid HTTPS)
- [ ] `get_appointed_resolver()` returns correct resolver + endpoint + `is_set: true`
- [ ] `is_authorized_resolver(resolver_address) == true`
- [ ] `resolve_claim` is blocked until appointed resolver is properly set
- [ ] Unauthorized address cannot call `resolve_claim`

### 2. Challenge Stake Forwarding (Non-Zero Required)
- [ ] `create_claim` → `resolve_claim`
- [ ] `challenge` with value ≥ `min_challenge_stake` (value = 0 must revert)
- [ ] Stake is persisted in `challenge_stakes`
- [ ] `StakeRecorded` event is emitted

### 3. Appeal Stake Forwarding (Non-Zero Required)
- [ ] Same flow as challenge
- [ ] `appeal` with value ≥ `min_appeal_stake` (value = 0 must revert)
- [ ] Stake recorded + `StakeRecorded` event

### 4. Human Review + On-chain Finalization (Mandatory)
- [ ] `create_claim` (hybrid mode enabled)
- [ ] `resolve_claim`
- [ ] `cast_human_vote("VALID")`
- [ ] After challenge window closes → `finalize_claim` succeeds
- [ ] Returns `{"success": true, "on_chain": true, "prisma_path_used": false}`
- [ ] Without sufficient human votes → reverts (no Prisma path allowed)

### 5. Resolver Stake Enforcement
- [ ] `add_resolver(non-owner)`
- [ ] Attempt `resolve_claim` without stake → fails
- [ ] `stake_as_resolver` with value ≥ `min_resolver_stake` → `resolve_claim` succeeds
