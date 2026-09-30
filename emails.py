# 10:50 AM 

'''
part 1 — normalize & count unique
normalization rules (applied to the local part, before the @):

remove all dots
ignore everything after a + sign
input: a list of email strings. output: the number of unique normalized emails.
example:

emails = ["test.email+spam@gmail.com", "testemail@gmail.com", "test.email@gmail.com"] → 1

'''

from enum import verify


def normalize_count(emails):
    normalized = set()

    for e in emails:
        e_normalized = ""
        for l in e:
            if l == '@' or l == '+':
                break
            else:
                if l == '.':
                    continue
                e_normalized += l
        normalized.add(e_normalized)
    return len(normalized)

# emails = ["test.email+spam@gmail.com", "testemail@gmail.com", "test.email@gmail.com"]
# A = normalize_count(emails)
# print(A)

'''
part 2 — find duplicate accounts
input: a list of (user_id, email) tuples. normalize each email, then group user ids by normalized email.
output: a dict mapping normalized_email → sorted list of user_ids, including only entries with more than one user.
example:

signups = [("u1", "test.email+spam@gmail.com"),
           ("u2", "testemail@gmail.com"),
           ("u3", "other@gmail.com")]
→ {"testemail@gmail.com": ["u1", "u2"]}

'''

def find_duplicates(signups):
    def normalize(e):
        e_normalized = ""
        for l in e:
            if l == '@' or l == '+':
                break
            else:
                if l == '.':
                    continue
                e_normalized += l
        return e_normalized

    emails_and_users = {}
    for user, email in signups:
        new_e = normalize(email)
        if new_e not in emails_and_users:
            emails_and_users[new_e] = [user]
        else:
            emails_and_users[new_e].append(user)
    
    results = {}
    for k, v in emails_and_users.items():
        if len(v) > 1:
            results[k] = v
    
    return results

signups = [("u1", "test.email+spam@gmail.com"),
           ("u2", "testemail@gmail.com"),
           ("u3", "other@gmail.com")]
        
# B = find_duplicates(signups)
# print(B)

'''
part 3 — verify new signups
existing registry (normalized email → list of user ids) plus a blocklist of normalized emails. process new (user_id, email) attempts in order, one decision each:

"rejected" — normalized email is in the blocklist
"duplicate" — normalized email already exists in the registry under a different user id
"accepted" — otherwise; register it so later attempts see it
output: a list of (user_id, decision) tuples, in attempt order.
example:

registry = {"testemail@gmail.com": ["u1", "u2"]}
blocked = {"badactor@gmail.com"}
attempts = [("u3", "test.email@gmail.com"),
            ("u4", "bad.actor+promo@gmail.com"),
            ("u5", "new.user@gmail.com"),
            ("u6", "newuser+spam@gmail.com")]
→ [("u3", "duplicate"), ("u4", "rejected"), ("u5", "accepted"), ("u6", "duplicate")]
'''

def verify_signup(attempts, registry, blocked):
    def normalize(e):
        e_normalized = ""
        for l in e:
            if l == '@' or l == '+':
                break
            else:
                if l == '.':
                    continue
                e_normalized += l
        return e_normalized
    
    normalized_blocked = []
    for e in blocked:
        normalized_blocked.append(normalize(e))
    
    registry_normalized = []
    for e in registry.keys():
        registry_normalized.append(normalize(e))
        
    results = []
    
    for user, email in attempts:
        new_e = normalize(email)
        if new_e not in registry_normalized and new_e not in normalized_blocked:
            results.append((user, "accepted"))
        elif new_e in registry_normalized:
            results.append((user, "duplicate"))
        elif new_e in normalized_blocked:
            results.append((user, "rejected"))
    
    return results 

registry = {"testemail@gmail.com": ["u1", "u2"]}
blocked = {"badactor@gmail.com"}
attempts = [("u3", "test.email@gmail.com"),
            ("u4", "bad.actor+promo@gmail.com"),
            ("u5", "new.user@gmail.com"),
            ("u6", "newuser+spam@gmail.com")]
# C = verify_signup(attempts, registry, blocked)
# print(C)

# 11:20 AM

'''
part 4 — merge accounts & detect conflicts
users can request merges: each (user_a, user_b) pair means "these two user ids belong to the same person." merges are transitive — use union-find.
after processing all merges, for each merged group compute:

representative: the lexicographically smallest user id in the group
emails: the sorted list of distinct normalized emails belonging to any user id in the group (look these up in the final registry from part 3, which includes accepted signups)
conflict: true if the group has more than one distinct normalized email (one "person" with two different canonical emails is suspicious)
details:
- only user ids appearing in at least one merge pair form groups; everyone else is ignored
- a user id in a merge pair might not exist in the registry (never signed up) — it still joins the group but contributes no emails
- a group whose members have zero emails total still gets reported, with an empty email list
output: a dict mapping representative_id → {"emails": [...], "conflict": bool}, sorted by representative id.
example:

registry = {"testemail@gmail.com": ["u1", "u2"],
            "newuser@gmail.com": ["u5", "u6"],
            "other@gmail.com": ["u3"]}
merges = [("u1", "u2"), ("u2", "u5"), ("u3", "u9")]
→ {
    "u1": {"emails": ["newuser@gmail.com", "testemail@gmail.com"], "conflict": True},
    "u3": {"emails": ["other@gmail.com"], "conflict": False},
  }
'''

from collections import defaultdict

def merge_and_conflict_detection(registry, merges):
    normalized_registry = {}

    def normalize(e):
        e_normalized = ""
        for l in e:
            if l == '@' or l == '+':
                break
            else:
                if l == '.':
                    continue
                e_normalized += l
        return e_normalized

    for email, users in registry.items():
        normalized_email = normalize(email)
        for u in users:
            if u not in normalized_registry:
                normalized_registry[u] = set()
            normalized_registry[u].add(normalized_email)

    parents = {}

    def find(x):
        if x not in parents:
            parents[x] = x
        if parents[x] == x:
            return x
        parents[x] = find(parents[x])
        return parents[x]

    for a, b in merges:
        parent_a = find(a)
        parent_b = find(b)
        
        if parent_a != parent_b:
            if parent_a < parent_b:
                parents[parent_b] = parent_a
            else:
                parents[parent_a] = parent_b

    all_users = set(parents.keys())
    for users in registry.values():
        all_users.update(users)

    groups = defaultdict(list)
    for u in all_users:
        groups[find(u)].append(u)

    results = {}
    conflicts = [] 

    for root, group_users in groups.items():
        group_emails = set()
        
        for u in group_users:
            if u in normalized_registry:
                group_emails.update(normalized_registry[u])
        
        if len(group_emails) > 1:
            conflicts.append(
                {"users": group_users, "emails": list(group_emails)}
            )
            
        results[root] = {
            "users": sorted(group_users),
            "emails": sorted(list(group_emails))
        }

    return results, conflicts

# 12:20 PM
