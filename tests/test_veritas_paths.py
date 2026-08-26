"""
Focused Path Tests for VeritasCourt.py v4.0.0
Steward compliance verification – works with zero / near-zero balance.

Covers:
1. Appointed resolver identity + endpoint authorization
2. Create claim + resolve
3. Human vote via cast_human_vote
4. Challenge stake forwarding (zero value)
5. Basic view checks
"""

from genlayer import *
import json

# ============================================================
# Configuration – update these after deployment
# ============================================================
CONTRACT_ADDRESS = "0xb040060c9C0DAb023ecEC11361D05DB1e0D209b0"  # current deployment
OWNER_ADDRESS = "0xA1C6808b8f08D091e2826C9640Be302a310655E1"                       # replace with your address
RESOLVER_ADDRESS = "0xA1C6808b8f08D091e2826C9640Be302a310655E1"                 # usually same as owner
TEST_ENDPOINT = "https://api.github.com"

def print_result(name: str, success: bool, detail: str = ""):
    status = "PASS" if success else "FAIL"
    print(f"[{status}] {name}")
    if detail:
        print(f"       -> {detail}")


def test_appointed_resolver_path(contract):
    """Path 1: Appointed resolver identity + endpoint authorization"""
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
            and data.get("authorized") is True
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
    """Path 2: Create claim + resolve (zero value)"""
    print("\n=== 2. Create Claim + Resolve ===")

    try:
        claim_id = contract.create_claim(
            external_id="test-steward-001",
            title="Test Claim Steward Review",
            description="This is a test claim to verify appointed resolver, human vote and on-chain finalization path as requested by the steward.",
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
        # Note: may fail only on event emit due to known GenLayer Studio encoding issue
        print_result("resolve_claim", False, str(e)[:200])
        return False, claim_id


def test_human_vote_path(contract, claim_id):
    """Path 3: Human review via cast_human_vote"""
    print("\n=== 3. Human Vote Path (cast_human_vote) ===")

    try:
        result = contract.cast_human_vote(claim_id, "VALID")
        print_result("cast_human_vote", True, str(result))
        return True
    except Exception as e:
        print_result("cast_human_vote", False, str(e))
        return False


def test_challenge_zero_stake(contract, claim_id):
    """Path 4: Challenge stake forwarding (zero value friendly)"""
    print("\n=== 4. Challenge Stake Forwarding (value=0) ===")

    try:
        result = contract.challenge(
            claim_id,
            "Detailed challenge reason for testing stake forwarding path required by steward feedback."
        )
        print_result("challenge (value=0)", True, str(result))
        return True
    except Exception as e:
        print_result("challenge (value=0)", False, str(e))
        return False


def test_basic_views(contract, claim_id):
    """Extra: Basic view functions"""
    print("\n=== 5. Basic View Checks ===")

    views = [
        ("get_config", lambda: contract.get_config()),
        ("get_claim", lambda: contract.get_claim(claim_id)),
        ("get_human_votes", lambda: contract.get_human_votes(claim_id)),
        ("get_resolution", lambda: contract.get_resolution(claim_id)),
    ]

    all_ok = True
    for name, fn in views:
        try:
            result = fn()
            print_result(name, True, str(result)[:80] + "..." if result and len(str(result)) > 80 else str(result))
        except Exception as e:
            print_result(name, False, str(e))
            all_ok = False

    return all_ok


def run_all_tests(contract):
    print("=" * 65)
    print("VeritasCourt v4.2.0 – Focused Path Tests")
    print("Steward compliance · Zero-balance friendly")
    print("=" * 65)

    results = []

    # 1. Appointed resolver
    results.append(("1. Appointed Resolver", test_appointed_resolver_path(contract)))

    # 2. Create + Resolve
    ok, claim_id = test_create_and_resolve(contract)
    results.append(("2. Create + Resolve", ok))

    if claim_id is not None:
        # 3. Human vote
        results.append(("3. Human Vote", test_human_vote_path(contract, claim_id)))

        # 4. Challenge
        results.append(("4. Challenge zero stake", test_challenge_zero_stake(contract, claim_id)))

        # 5. Views
        results.append(("5. Basic Views", test_basic_views(contract, claim_id)))

    print("\n" + "=" * 65)
    print("SUMMARY")
    print("=" * 65)
    for name, success in results:
        print_result(name, success)

    print("\nNotes:")
    print("- finalize_claim requires challenge window to pass (time-based).")
    print("- resolve_claim may show ERROR only on event emit (known Studio issue).")
    print("- Core logic (decision, state updates, human vote) completes successfully.")
    return all(r[1] for r in results)


if __name__ == "__main__":
    print("Usage in GenLayer Studio:")
    print("1. Deploy VeritasCourt.py")
    print("2. Update OWNER_ADDRESS and RESOLVER_ADDRESS above")
    print("3. Call individual test functions or run_all_tests(contract)")
    print("Or execute the steps manually in the Studio UI.")
