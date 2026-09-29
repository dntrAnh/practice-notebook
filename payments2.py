class PaymentStateMachine:
    """
    Payment lifecycle as an explicit state machine.

    States: None (unseen) -> created -> authorized -> partially_captured* -> successful -> refunded
    Valid moves are looked up by (current_status, action) in TRANSITIONS;
    anything not in the table is out-of-order/invalid and gets ignored.
    """

    def __init__(self):
        self.events = []
        self.states = {}
        self.merchants = {}  # merchant_id -> {"risk_score": int, "blocked": bool}

    def process_events(self,
                       event_id,
                       event_time,
                       event_type,
                       payment_id,
                       payment_event_type,
                       merchant_id,
                       amount):
        self.events.append({
            "event_id": event_id,
            "event_time": event_time,
            "event_type": event_type,
            "payment_id": payment_id,
            "payment_event_type": payment_event_type,
            "merchant_id": merchant_id,
            "amount": amount,
        })

    def _is_merchant_blocked(self, merchant_id):
        return self.merchants.get(merchant_id, {}).get("blocked", False)

    def _handle_merchant_update(self, event):
        merchant_id = event["merchant_id"]
        risk_score = event["amount"]
        if not isinstance(risk_score, int) or not (0 <= risk_score <= 100):
            print(f"Unexpected risk score: {risk_score} for merchant_id: {merchant_id}")
            return
        merchant = self.merchants.setdefault(merchant_id, {"risk_score": risk_score, "blocked": False})
        merchant["risk_score"] = risk_score
        if risk_score >= 80 and not merchant["blocked"]:
            merchant["blocked"] = True
            print(f"Merchant blocked due to high risk score: {merchant_id}")

    # -- transition handlers ------------------------------------------------
    # Each takes (self, state, event) where state is None if the payment
    # hasn't been created yet, and returns a dict of fields to merge into the
    # payment's record, or None to reject/ignore the event.

    def _create(self, state, event):
        return {
            "event_time": event["event_time"],
            "status": "created",
            "payment_id": event["payment_id"],
            "merchant_id": event["merchant_id"],
            "authorized_amount": 0,
            "captured_amount": 0,
        }

    def _authorize(self, state, event):
        if self._is_merchant_blocked(state["merchant_id"]):
            print(f"Ignoring authorize for blocked merchant: {state['merchant_id']} (payment_id: {state['payment_id']})")
            return None
        return {
            "status": "authorized",
            "event_time": event["event_time"],
            "authorized_amount": state["authorized_amount"] + event["amount"],
        }

    def _capture(self, state, event):
        captured_amount = state["captured_amount"] + event["amount"]
        if captured_amount > state["authorized_amount"]:
            print(f"Unexpected: captured amount exceeds authorized amount for payment_id: {state['payment_id']}")
            return None
        if captured_amount == state["authorized_amount"]:
            print(f"Payment fully captured for payment_id: {state['payment_id']}")
            status = "successful"
        else:
            print(f"Payment partially captured for payment_id: {state['payment_id']}")
            status = "partially_captured"
        return {"status": status, "event_time": event["event_time"], "captured_amount": captured_amount}

    def _refund(self, state, event):
        print(f"Payment refunded for payment_id: {state['payment_id']}")
        return {"status": "refunded", "event_time": event["event_time"]}

    # Valid (current_status, action) pairs -> handler. current_status is None
    # to mean "payment not seen yet" (only "create" is valid there).
    TRANSITIONS = {
        (None, "create"): _create,
        ("created", "authorize"): _authorize,
        ("authorized", "authorize"): _authorize,
        ("authorized", "capture"): _capture,
        ("partially_captured", "capture"): _capture,
        ("successful", "refund"): _refund,
    }

    def aggregate(self):
        for event in self.events:
            if event["event_type"] == "merchant_update":
                self._handle_merchant_update(event)
                continue

            payment_id = event["payment_id"]
            action = event["payment_event_type"]
            state = self.states.get(payment_id)
            current_status = state["status"] if state else None

            handler = self.TRANSITIONS.get((current_status, action))
            if handler is None:
                print(f"Unexpected event type: {action} for payment_id: {payment_id}")
                continue

            updates = handler(self, state, event)
            if updates is None:
                continue

            if state is None:
                self.states[payment_id] = updates
            else:
                state.update(updates)


def _build_system(events):
    system = PaymentStateMachine()
    for event in events:
        system.process_events(*event)
    system.aggregate()
    return system
