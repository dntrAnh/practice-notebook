def interval_pattern_sorting(intervals):
    if not intervals:
        return []
    
    # 1. Sort intervals primarily by start time, secondarily by end time
    intervals.sort(key=lambda x: x[0])
    
    # 2. Initialize your tracking variables (e.g., current merged interval, counter, etc.)
    merged = [intervals[0]]
    
    # 3. Iterate through the rest of the intervals
    for current in intervals[1:]:
        prev = merged[-1]
        
        # Example condition: Check for overlap
        if prev[1] >= current[0]:
            # Do something when they overlap (e.g., merge them)
            prev[1] = max(prev[1], current[1])
        else:
            # Do something when they don't overlap (e.g., add new interval)
            merged.append(current)
            
    return merged