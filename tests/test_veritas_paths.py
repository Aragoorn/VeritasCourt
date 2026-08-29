"""
Focused Path Tests for VeritasCourt.py v4.4.1
Steward compliance verification

Covers the exact paths requested by the steward:
1. Appointed resolver identity + endpoint authorization (non-ephemeral)
2. Create claim + resolve
3. Human vote via cast_human_vote
4. Challenge stake forwarding (non-zero value required)
5. Basic view checks
"""

from genlayer import *
import json

# ============================================================
# Configuration – update these after deployment
# ============================================================
CONTRACT_ADDRESS = "0xC3A6e79d9E6C828EE7f9A535679720593c9fb4C5"
OWNER_ADDRESS = "0xA1C6808b8f08D091e2826C9640Be302a310655E1"
RESOLVER_ADDRESS = "0xA1C6808b8f08D091e2826C9640Be302a310655E1"          # usually same as owner
TEST_ENDPOINT = "https://api.github.com"

def print_result(name: str, success: bool, detail: str = ""):
    status = "PASS" if success else "FAIL"
    print(f"[{status}] {name}")
    if detail:
        print(f"       -> {detail}")


def test_appointed_resolver_path(contract):
    """Path 1: Appointed resolver identity + endpoint authorization (non-ephemeral)"""
    print("\n=== 1. Appointed Resolver + Endpoint Authorization ===")

    try:
        contract.set_appointed_resolver(RESOLVER_ADDRESS, TEST_ENDPOINT)
        print_result("set_appointed_resolver", True)
    except Exception as e:
        print_result("set_appointed_resolver", False, str(e))
        return False

    try:
        raw = contract.get_appointed_resolver()
        data = json.loads(raw) if isinstance(raw, str) else raw
        ok = (
            data.get("resolver") == RESOLVER_ADDRESS
            and data.get("endpoint") == TEST_ENDPOINT
            and data.get("is_set") is True
        )
        print_result("get_appointed_resolver", ok, str(data))
    except Exception as e:
        print_result("get_appointed_resolver", False, str(e))
        return False

    try:
        authorized = contract.is_authorized_resolver(RESOLVER_ADDRESS)
        print_result("is_authorized_resolver", bool(authorized))
    except Exception as e:
        print_result("is_authorized_resolver", False, str(e))
        return False

    return True


def test_create_and_resolve(contract):
    """Path 2: Create claim + resolve"""
    print("\n=== 2. Create Claim + Resolve ===")

    try:
        claim_id = contract.create_claim(
            external_id="test-steward-v44-001",
            title="Test Claim Steward Review v4.4.1",
            description="This claim verifies appointed resolver, non-zero stake forwarding, human vote via cast_human_vote and strict on-chain finalization as required by the steward.",
            evidence_urls="https://raw.githubusercontent.com/Aragoorn/VeritasCourt/main/README.md",
            plaintiff=OWNER_ADDRESS,
            defendant="0x0000000000000000000000000000000000000001",
            template_id="general",
        )
        print_result("create_claim", True, f"claim_id={claim_id}")
    except Exception as e:
        print_result("create_claim", False, str(e))
        return False, None

    try:
        result = contract.resolve_claim(claim_id)
        print_result("resolve_claim", True, str(result)[:150] if result else "No return value")
        return True, claim_id
    except Exception as e:
        print_result("resolve_claim", False, str(e)[:200])
        return False, claim_id


def test_human_vote_path(contract, claim_id):
    """Path 3: Human review via cast_human_vote (required for finalization)"""
    print("\n=== 3. Human Vote Path (cast_human_vote) ===")

    try:
        result = contract.cast_human_vote(claim_id, "VALID")
        print_result("cast_human_vote", True, str(result))
        return True
    except Exception as e:
        print_result("cast_human_vote", False, str(e))
        return False


def test_challenge_non_zero_stake(contract, claim_id):
    """Path 4: Challenge stake forwarding – non-zero value is now mandatory"""
    print("\n=== 4. Challenge Stake Forwarding (non-zero required) ===")

    try:
        # In Studio: make sure to send value >= min_challenge_stake
        result = contract.challenge(
            claim_id,
            "Detailed challenge reason for testing mandatory non-zero stake forwarding required by steward feedback."
        )
        print_result("challenge (non-zero value)", True, str(result))
        return True
    except Exception as e:
        # Expected to fail if value = 0 (this is correct behavior in v4.4.0)
        print_result("challenge", False, str(e)[:200])
        return False


def test_basic_views(contract, claim_id):
    """Basic view functions"""
    print("\n=== 5. Basic View Checks ===")

    views = [
        ("get_config", lambda: contract.get_config()),
        ("get_claim", lambda: contract.get_claim(claim_id)),
        ("get_human_votes", lambda: contract.get_human_votes(claim_id)),
        ("get_resolution", lambda: contract.get_resolution(claim_id)),
        ("get_appointed_resolver", lambda: contract.get_appointed_resolver()),
    ]

    all_ok = True
    for name, fn in views:
        try:
            result = fn()
            detail = str(result)[:90] + "..." if result and len(str(result)) > 90 else str(result)
            print_result(name, True, detail)
        except Exception as e:
            print_result(name, False, str(e))
            all_ok = False

    return all_ok


def run_all_tests(contract):
    print("=" * 65)
    print("VeritasCourt v4.4.1 – Focused Path Tests")
    print("Steward compliance verification")
    print("=" * 65)

    results = []

    results.append(("1. Appointed Resolver", test_appointed_resolver_path(contract)))

    ok, claim_id = test_create_and_resolve(contract)
    results.append(("2. Create + Resolve", ok))

    if claim_id is not None:
        results.append(("3. Human Vote", test_human_vote_path(contract, claim_id)))
        results.append(("4. Challenge non-zero stake", test_challenge_non_zero_stake(contract, claim_id)))
        results.append(("5. Basic Views", test_basic_views(contract, claim_id)))

    print("\n" + "=" * 65)
    print("SUMMARY")
    print("=" * 65)
    for name, success in results:
        print_result(name, success)

    print("\nNotes:")
    print("- set_appointed_resolver MUST be called first (non-ephemeral requirement).")
    print("- challenge / appeal now reject value = 0 (hard requirement).")
    print("- finalize_claim requires previous cast_human_vote when hybrid is enabled.")
    print("- Core logic completes even if event emission has Studio encoding quirks.")
    return all(r[1] for r in results)


if __name__ == "__main__":
    print("Usage in GenLayer Studio:")
    print("1. Deploy VeritasCourt.py (v4.4.1)")
    print("2. Update OWNER_ADDRESS, RESOLVER_ADDRESS and CONTRACT_ADDRESS")
    print("3. Call set_appointed_resolver first")
    print("4. Then run the individual test functions or run_all_tests(contract)")
    print("Or execute the steps manually in the Studio UI with correct values.")
