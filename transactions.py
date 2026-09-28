'''
problem: parsing and evaluating stripe transaction logs

part 1 — parse & compute balances
input: a list of strings, each line has the format "user event amount", where event is either deposit or withdraw. deposit adds money, withdraw subtracts it.
output: a dict mapping user → final balance.
example:

logs = ["alice deposit 100", "bob deposit 50", "alice withdraw 30"]
→ {"alice": 70, "bob": 50}

'''

'''
part 2 — transfers & failed operations
new event transfer with a different format: "user transfer target amount" (subtract from user, add to target).
new rule: if a withdraw or transfer exceeds the user's current balance, skip that transaction and count 1 failed operation for that user.
output: a tuple (balances, failed) where failed maps user → number of skipped transactions.
example:

logs = ["alice deposit 100", "alice transfer bob 40", "bob withdraw 80", "bob withdraw 10"]
→ balances {"alice": 60, "bob": 30}, failed {"bob": 1}
(bob's withdraw of 80 is skipped — he only had 40 at that point)
'''

'''
part 3 — flag suspicious users
two new parameters k and t. after processing all logs, flag a user as suspicious if either holds:
- failed transactions > k
- total amount the user transferred out > t
output: a sorted list of suspicious user ids.
example with k=1, t=100:

logs = ["alice deposit 200", "alice transfer bob 120", "bob withdraw 200", "bob withdraw 200"]
→ ["alice", "bob"]
(alice transferred out 120 > 100; bob failed twice > 1)

'''

from collections import defaultdict

def update_account(transactions, k, t):
    # transactions = ongoing transaction 
    # k = cap number of failed transactions 
    # t = cap amount can be transferred 

    balances = defaultdict(int)
    failed = defaultdict(int)
    transferred_out = defaultdict(int)
    flags = []
    
    for trans in transactions:
        transaction = trans.split()

        # always available: user, event, amount
        # not always: target 
        user, event, target, amount = "", "", "", 0
        
        # transaction is withdraw/deposit
        if len(transaction) == 3:
            user, event, amount = transaction[0], transaction[1], int(transaction[2])
        # transaction is transfer
        elif len(transaction) == 4:
            user, event, target, amount = transaction[0], transaction[1], transaction[2], int(transaction[3])
        
        # transaction ongoing
        if event == "deposit":
            balances[user] += amount
        elif event == "withdraw":
            # invalid amount 
            if amount > balances[user]: 
                failed[user] += 1
            else:
                balances[user] -= amount 
        elif event == "transfer":
            # invalid amount
            if amount > balances[user]: 
                failed[user] += 1
            else:
                balances[user] -= amount
                transferred_out[user] += amount
                balances[target] += amount 
        
        # flag suspicious users 
        if failed[user] > k and user not in flags:
            flags.append(user)
        elif transferred_out[user] > t and user not in flags:
            flags.append(user)
    
    return dict(balances), dict(failed), sorted(flags)

UA = update_account(["alice deposit 200", "alice transfer bob 120", "bob withdraw 200", "bob withdraw 200"], 1, 100)
print(UA)
