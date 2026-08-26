"""
Focused Path Tests for VeritasCourt.py v4.0.0
Steward compliance verification – works with zero/near-zero balance.
"""

from genlayer import *
import json

# ============================================================
# Configuration – update these after deployment
# ============================================================
CONTRACT_ADDRESS = "0xb040060c9C0DAb023ecEC11361D05DB1e0D209b0"  # update if new deploy
OWNER_ADDRESS = "0xA1C6808b8f08D091e2826C9640Be302a310655E1"          # replace with your address
RESOLVER_ADDRESS = "0xaa5Eaa814bD58e5079Db20FB0826D2727c926b9E"    # usually same as owner for testing
TEST_ENDPOINT = "https://api.github.com"

def print_result(name: str, success: bool, detail: str = ""):
    status = "PASS" if success else "FAIL"
    print(f"[{status}] {name}")
    if detail:
        print(f"       -> {detail}")


def test_appointed_resolver_path(contract):
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
    print("\n=== 2. Create Claim + Resolve (zero value) ===")
    try:
        claim_id = contract.create_claim(
            external_id="test-001",
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
        print_result("resolve_claim", True, str(result)[:120])
        return True, claim_id
    except Exception as e:
        print_result("resolve_claim", False, str(e))
        return False, claim_id


def test_human_vote_path(contract, claim_id):
    print("\n=== 3. Human Vote Path ===")
    try:
        result = contract.cast_human_vote(claim_id, "VALID")
        print_result("cast_human_vote", True, str(result))
        return True
    except Exception as e:
        print_result("cast_human_vote", False, str(e))
        return False


def test_challenge_zero_stake(contract, claim_id):
    print("\n=== 4. Challenge with zero stake ===")
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


def run_all_tests(contract):
    print("=" * 60)
    print("VeritasCourt v4.2.0 – Focused Path Tests (zero balance friendly)")
    print("=" * 60)

    results = []
    results.append(("Appointed Resolver", test_appointed_resolver_path(contract)))

    ok, claim_id = test_create_and_resolve(contract)
    results.append(("Create + Resolve", ok))

    if claim_id is not None:
        results.append(("Human Vote", test_human_vote_path(contract, claim_id)))
        results.append(("Challenge zero stake", test_challenge_zero_stake(contract, claim_id)))

    print("\n" + "=" * 60)
    print("SUMMARY")
    for name, success in results:
        print_result(name, success)

    print("\nNote: finalize_claim needs challenge window to pass.")
    return all(r[1] for r in results)


if __name__ == "__main__":
    print("In GenLayer Studio: deploy the contract, then call the individual test functions manually.")
    print("Or attach this script after loading the contract instance.")
