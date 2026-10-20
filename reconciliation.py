from typing import List

class Solution:
    def reconcilePayment(self, payment: str, invoices: List[str], forgiveness: int) -> str:
        """
        You are reconciling a single incoming payment against a list of open invoices.
        Decide which invoice the payment settles by applying matching rules in strict priority order,
        and return a human-readable result string.
        """
        details = payment.split(',')
        pay_id, amt = details[0].strip(), int(details[1].strip())
        memo = ", ".join(details[2:]).strip()
        
        parsed_invoices = []
        
        for inv_str in invoices:
            parts = inv_str.split(',')
            parsed_invoices.append({
                "raw": inv_str,
                "id": parts[0].strip(),
                "date": parts[1].strip(),
                "amount": int(parts[2].strip())
            })
            
        id_candidates = []
        for inv in parsed_invoices:
            if self.id_match(inv["id"], memo):
                id_candidates.append(inv)
        if id_candidates:
            id_candidates.sort(key=lambda x:x["date"])
            best = id_candidates[0]
            return f"Payment {pay_id} paid {amt} for invoice {best['id']} due on {best['date']}"
        
        exact_candidates = []
        for inv in parsed_invoices:
            if self.amount_match(amt, inv["amount"]):
                exact_candidates.append(inv)
        if exact_candidates:
            exact_candidates.sort(key=lambda x:x["date"])
            best = exact_candidates[0]
            return f"Payment {pay_id} paid {amt} for invoice {best['id']} due on {best['date']}"
        
        if forgiveness > 0:
            fuzzy = []
            for inv in parsed_invoices:
                if inv["amount"] == amt:
                    continue
                if self.inclusive_range(inv["amount"], amt, forgiveness):
                    fuzzy.append(inv)
            if fuzzy:
                fuzzy.sort(key=lambda x:x["date"])
                best = fuzzy[0]
                return f"Payment {pay_id} paid {amt} for invoice {best['id']} due on {best['date']}"

        return f"Payment {pay_id} could not be matched to any invoice"
    
    def id_match(self, inv_id, memo):
        memo_lower = memo.lower()
        for marker in ["paying for:", "paying off:"]:
            idx = memo_lower.find(marker)
            if idx != -1:
                target = memo[idx + len(marker):].strip()
                if target == inv_id:
                    return True 
        return False 
    
    def amount_match(self, amount, invoice_amount):
        return amount == invoice_amount
    
    def inclusive_range(self, invoice_amount, amount, forgiveness):
        lower = amount - forgiveness
        upper = amount + forgiveness
        return lower <= invoice_amount <= upper

# ==========================================
# Test Cases for Local Verification
# ==========================================
if __name__ == "__main__":
    sol = Solution()
    
    # Example 1
    res1 = sol.reconcilePayment(
        payment="pay_1, 100, paying for: INV-7",
        invoices=["INV-7, 2026-03-01, 250", "INV-3, 2026-02-01, 100"],
        forgiveness=0
    )
    print("Example 1:", res1)
    # Expected: "Payment pay INV-7 _1 paid 100 for invoicedue on 2026-03-01"

    # Example 2
    res2 = sol.reconcilePayment(
        payment="pay_2, 100, March rent, thanks",
        invoices=["INV-9, 2026-04-01, 100", "INV-4, 2026-01-15, 100"],
        forgiveness=0
    )
    print("Example 2:", res2)
    # Expected: "Payment pay_2 paid 100 for invoice INV-4 due on 2026-01-15"

    # Example 3
    res3 = sol.reconcilePayment(
        payment="pay_3, 98, bank transfer",
        invoices=["INV-1, 2026-05-01, 100", "INV-2, 2026-06-01, 130"],
        forgiveness=2
    )
    print("Example 3:", res3)
    # Expected: "Payment pay_3 paid 98 for invoice INV-1 due on 2026-05-01"

    # Example 4
    res4 = sol.reconcilePayment(
        payment="pay_4, 500, no matching invoice here",
        invoices=["INV-1, 2026-05-01, 100", "INV-2, 2026-06-01, 130"],
        forgiveness=0
    )
    print("Example 4:", res4)
    # Expected: "Payment pay_4 could not be matched to any invoice"