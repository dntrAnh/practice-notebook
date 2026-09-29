VALID = {
    "non-existent": {"create"},
    "created": {"authorize"},
    "authorized": {"authorize", "capture"},
    "partially_captured": {"capture"},
    "successful": {"refund"},
    "refunded": "",
}
from collections import defaultdict 

def process_events(transactions):
    payments = defaultdict(lambda: {
        "merchant_id": "",
        "amount_authorized": 0,
        "amount_captured": 0,
        "last_event_at": 0,
        "state": "non-existent"
    })
    blocked = set()
    order = []
    seen = set()

    for t in transactions:
        parts = t.split(',') if isinstance(t, str) else t
        eid, e_time, e_type, pay_id, pay_e_type, merchant_id, amt = parts

        if eid in seen:
            continue
        seen.add(eid)

        if e_type == "merchant_update":
            if int(amt) >= 80:
                blocked.add(merchant_id)
            continue

        current = payments[pay_id]

        if e_type == "payment": 
            curr_state = current["state"]
            
            if pay_e_type not in VALID[curr_state]:
                continue
            
            if pay_id not in order:
                order.append(pay_id)

            current["last_event_at"] = e_time

            if pay_e_type == "create":
                current["merchant_id"] = merchant_id
                current["state"] = "created"
            elif pay_e_type == "authorize" and current["merchant_id"] not in blocked:
                if amt != "-": 
                    current["amount_authorized"] += int(amt)
                current["state"] = "authorized"
            elif pay_e_type == "capture":
                if amt != "-":
                    current["amount_captured"] += int(amt)
                if current["amount_captured"] == current["amount_authorized"]:
                    current["state"] = "successful"
                else:
                    current["state"] = "partially_captured"
        elif e_type == "refund":
            if current["state"] != "refunded": 
                current["state"] = "refunded"
                current["last_event_at"] = e_time 


    result = []
    for pid in order:
        info = payments[pid]
        res = f"{pid},{info['merchant_id']},{info['state']},{info['amount_authorized']},{info['amount_captured']},{info['last_event_at']}"
        result.append(res)
    
    return result

events = [
    "evt_1,0,payment,payment_1,create,merchant_1,-",
    "evt_2,1,payment,payment_1,authorize,-,10",
    "evt_3,2,merchant_update,-,-,merchant_1,85",
    "evt_4,3,payment,payment_2,create,merchant_1,-",
    "evt_5,4,payment,payment_2,authorize,-,20",
    "evt_6,5,payment,payment_1,capture,-,10",
    "evt_7,6,merchant_update,-,-,merchant_1,10"
]

for row in process_events(events):
    print(row)
