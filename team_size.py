'''
Problem: Maximum Interactive Team Size
Platform: Microsoft OA (Medium)

You are given n employees. Employee i works during the closed interval [startTime[i], endTime[i]].

Two employees can interact when their working intervals overlap. A team is valid when at least one employee in that team can interact with every other team member. The other team members do not need to interact with one another.

Return the maximum possible size of a valid team. An employee is included in their own team, so the answer is at least 1.

Function Signature:
getMaximumTeamSize(startTime: int[], endTime: int[]) -> int

Constraints:
- 1 <= startTime.length == endTime.length <= 200,000
- 0 <= startTime[i] <= endTime[i] <= 10^9
- Intervals that share an endpoint overlap.

Examples:

Example 1:
startTime = [1, 6, 4, 3, 1]
endTime   = [2, 7, 5, 8, 2]
Return: 3
Explanation: Employees 1, 2, and 3 form a valid team because employee 3, working from 3 through 8, overlaps both other intervals.

Example 2:
startTime = [1, 2, 3]
endTime   = [5, 4, 3]
Return: 3
Explanation: All three intervals contain time 3, so any employee can serve as the member who interacts with everyone.

Example 3:
startTime = [1, 4, 7]
endTime   = [2, 5, 8]
Return: 1
Explanation: No two employees overlap, so every valid team contains only its central employee.
'''

def find_team_size(startTime, endTime):
    combined = []
    for i in range(len(startTime)):
        combined.append([startTime[i], endTime[i]])
        
    combined.sort(key = lambda x:x[0])
    n = len(combined)
    max_team = 1
    
    for i in range(n):
        hub_start, hub_end = combined[i]
        curr_size = 0
        for j in range(n):
            other_start, other_end = combined[j]
            if max(hub_start, other_start) <= min(hub_end, other_end):
                curr_size += 1
        max_team = max(max_team, curr_size)
    
    return max_team
    

Find = find_team_size([1, 6, 4, 3, 1], [2, 7, 5, 8, 2])
print(Find)