"""Core Ephemeral Credential Vault Proxy implementation."""
import time
import secrets
from typing import Dict, Optional, Tuple, Any, Callable


class EphemeralTicket:
    def __init__(self, ticket_id: str, service: str, ttl_seconds: float = 60.0):
        self.ticket_id = ticket_id
        self.service = service
        self.expires_at = time.time() + ttl_seconds
        self.is_used = False


class EphemeralVaultProxy:
    def __init__(self):
        self.master_secrets: Dict[str, str] = {}  # service -> real_secret
        self.active_tickets: Dict[str, EphemeralTicket] = {}

    def store_master_secret(self, service: str, secret_key: str):
        self.master_secrets[service] = secret_key

    def vend_ticket(self, service: str, ttl_seconds: float = 60.0) -> str:
        if service not in self.master_secrets:
            raise KeyError(f"Service '{service}' has no stored master secret")
        t_id = f"tkt_{secrets.token_hex(8)}"
        ticket = EphemeralTicket(t_id, service, ttl_seconds)
        self.active_tickets[t_id] = ticket
        return t_id

    def execute_with_ticket(
        self,
        ticket_id: str,
        target_fn: Callable[[str, Dict[str, Any]], Any],
        payload: Dict[str, Any]
    ) -> Tuple_Result:
        ticket = self.active_tickets.get(ticket_id)
        if not ticket:
            return False, "Invalid or expired ticket"

        if ticket.is_used:
            return False, "Ticket has already been consumed (single-use policy)"

        if time.time() > ticket.expires_at:
            del self.active_tickets[ticket_id]
            return False, "Ticket expired"

        # Mark consumed immediately
        ticket.is_used = True
        real_key = self.master_secrets[ticket.service]

        try:
            result = target_fn(real_key, payload)
            del self.active_tickets[ticket_id]
            return True, result
        except Exception as e:
            del self.active_tickets[ticket_id]
            return False, f"Execution failed: {e}"


Tuple_Result = Any
