"""Unit tests for ephemeral-credential-vault-proxy."""
import unittest
from ephemeral_credential_vault_proxy.vault import EphemeralVaultProxy


class TestEphemeralVaultProxy(unittest.TestCase):
    def setUp(self):
        self.vault = EphemeralVaultProxy()
        self.vault.store_master_secret("github", "ghp_super_secret_token")

    def test_single_use_enforcement(self):
        tkt = self.vault.vend_ticket("github")
        ok, res = self.vault.execute_with_ticket(tkt, lambda k, p: "success", {})
        self.assertTrue(ok)
        self.assertEqual(res, "success")

        # Second use must fail
        ok2, _ = self.vault.execute_with_ticket(tkt, lambda k, p: "success", {})
        self.assertFalse(ok2)
