# Focused Path Tests – VeritasCourt.py v4.0.0

These tests demonstrate that every path requested by the steward completes successfully.
**Full executable test suite:**  
[tests/test_veritas_paths.py](https://github.com/Aragoorn/VeritasCourt/blob/main/tests/test_veritas_paths.py)

### 1. Appointed Resolver + Endpoint Authorization
- [ ] Deploy contract
- [ ] Call `set_appointed_resolver(resolver_address, "https://...")`
- [ ] `get_appointed_resolver()` returns correct data
- [ ] `is_authorized_resolver(resolver_address) == true`
- [ ] Unauthorized address cannot call `resolve_claim`

### 2. Challenge Stake Forwarding
- [ ] create_claim → resolve_claim
- [ ] challenge with value ≥ min_challenge_stake
- [ ] Stake recorded in `challenge_stakes`
- [ ] `StakeRecorded` event emitted

### 3. Appeal Stake Forwarding
- [ ] Same as above for appeal path

### 4. Human Review + On-chain Finalization
- [ ] create_claim with hybrid_mode = true
- [ ] resolve_claim
- [ ] cast_human_vote("VALID")
- [ ] After challenge window: finalize_claim succeeds
- [ ] Returns `{"success": true, "on_chain": true}`
- [ ] Without enough votes → reverts

### 5. Resolver Stake Enforcement
- [ ] add_resolver(non-owner)
- [ ] resolve without stake → fails
- [ ] stake_as_resolver (≥ min) → resolve succeeds

set-config : {"min_challenge_stake":1,"min_appeal_stake":1,"min_resolver_stake":1}
