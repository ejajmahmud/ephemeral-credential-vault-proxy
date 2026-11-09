"""CLI for ephemeral-credential-vault-proxy."""
import sys
import argparse
from .vault import EphemeralVaultProxy


def dummy_api_call(secret_key: str, payload: dict) -> str:
    return f"Authenticated with key len {len(secret_key)}, processed: {payload}"


def main():
    parser = argparse.ArgumentParser(description="Ephemeral Credential Vault Proxy CLI")
    parser.add_argument("--demo", action="store_true", help="Run ephemeral credential vending demo")
    args = parser.parse_args()

    if args.demo:
        vault = EphemeralVaultProxy()
        vault.store_master_secret("stripe", "sk_live_master_secret_key_12345")

        tkt = vault.vend_ticket("stripe")
        print(f"Vended Ephemeral Ticket: {tkt}")

        ok, res = vault.execute_with_ticket(tkt, dummy_api_call, {"amount": 5000})
        print(f"Execution 1: Success={ok} | {res}")

        # Try to reuse the single-use ticket
        ok2, res2 = vault.execute_with_ticket(tkt, dummy_api_call, {"amount": 5000})
        print(f"Execution 2 (Replay Attempt): Success={ok2} | Reason: {res2}")
    else:
        parser.print_help()
    sys.exit(0)


if __name__ == "__main__":
    main()
