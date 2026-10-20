from typing import List
import math 

class Solution:
    def solveRequestRoutingSystem(self, input: str) -> List[str]:
        """
        You are building a request-routing command processor for datacenters. 
        The function receives the complete newline-separated input as one string 
        and returns one output string per command.
        """
        # TODO: Implement your solution here
        centers = {}
        results = []
        for i in input.split('\n'):
            command = i.split(' ')
            if command[0] == 'REGISTER':
                results.append(self.register_center(centers, command[1], command[2], command[3], command[4]))
            elif command[0] == 'SET_HEALTHY':
                results.append(self.set_healthy(centers, command[1], command[2]))
            elif command[0] == 'DISTANCE':
                results.append(self.compute_distance(command[1], command[2], command[3], command[4]))
            elif command[0] == 'ROUTE':
                results.append(self.find_healthy(centers, command[1], command[2]))
                
        return results

    def valid_lat_lon(self,lat, lon):
        lat, lon = int(lat), int(lon)
        if -90 <= lat <= 90 and -180 <= lon <= 180:
            return True 
        return False 
    
    def register_center(self, centers, name, lat, lon, cap):
        lat, lon, cap = int(lat), int(lon), int(cap)
        if name in centers or not self.valid_lat_lon(lat, lon) or cap <= 0:
            return "ERROR"
        
        centers[name] = {
            'lat': lat,
            'lon': lon,
            'cap': cap,
            'healthy': True,
            'load': 0
        }
        return "OK"
    
    def set_healthy(self, centers, name, value):
        if name not in centers:
            return "ERROR"
        value = value.lower()
        if value == 'true':
            centers[name]['healthy'] = True 
            return "OK"
        elif value == 'false':
            centers[name]['healthy'] = False
            return "OK"
        return "ERROR"
    
    def compute_distance(self, lat1, lon1, lat2, lon2):
        if not self.valid_lat_lon(lat1, lon1) or not self.valid_lat_lon(lat2, lon2):
            return "ERROR"
        lat1, lat2 = int(lat1), int(lat2)
        lon1, lon2 = int(lon1), int(lon2)
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)
        
        a = math.sin(dphi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return str(round(6371 * c))

    def find_healthy(self, centers, lat, lon):
        if not self.valid_lat_lon(lat, lon):
            return "ERROR"
        
        target_lat, target_lon = float(lat), float(lon)
        
        healthy_nodes = []
        
        for name, data in centers.items():
            if data['healthy'] == True:
                phi1, phi2 = math.radians(target_lat), math.radians(data['lat'])
                dphi = math.radians(data['lat'] - target_lat)
                dlambda = math.radians(data['lon'] - target_lon)
                
                a = math.sin(dphi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2)**2
                c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
                exact_dist = 6371 * c
                
                healthy_nodes.append({
                    'name': name,
                    'exact_dist': exact_dist,
                    'rounded_dist': round(exact_dist)
                })
        
        if not healthy_nodes:
            return "None"
        
        healthy_nodes.sort(key=lambda x: (x['exact_dist'], x['name']))
        
        result = ','.join([node['name'] for node in healthy_nodes])
        
        chosen = None 
        for node in healthy_nodes:
            name = node['name']
            if centers[name]['load'] < centers[name]['cap']:
                chosen = node
                centers[name]['load'] += 1
                break
        
        if chosen: 
            return f"{chosen['name']} {chosen['rounded_dist']} {result}"
        else:
            return f"None {result}"

# ==========================================
# Test Cases for Local Verification
# ==========================================
if __name__ == "__main__":
    sol = Solution()
    
    # Example 1
    input_str_1 = (
        "REGISTER us-west 38 -122 100\n"
        "REGISTER us-east 41 -74 150\n"
        "REGISTER us-west 50 -100 50\n"
        "REGISTER invalid-node 91 0 100\n"
        "REGISTER invalid-cap 0 0 0\n"
        "SET_HEALTHY us-east false\n"
        "SET_HEALTHY fake-node true"
    )
    res1 = sol.solveRequestRoutingSystem(input_str_1)
    print("Example 1:", res1)
    # Expected: ["OK", "OK", "ERROR", "ERROR", "ERROR", "OK", "ERROR"]

    # Example 2
    input_str_2 = (
        "DISTANCE 38 -122 41 -74\n"
        "DISTANCE 0 0 0 0\n"
        "DISTANCE 91 0 0 0"
    )
    res2 = sol.solveRequestRoutingSystem(input_str_2)
    print("Example 2:", res2)
    # Expected: ["4080", "0", "ERROR"]

    # Example 3
    input_str_3 = (
        "REGISTER node-A 0 0 1\n"
        "REGISTER node-B 0 0 1\n"
        "REGISTER node-C 10 10 100\n"
        "SET_HEALTHY node-C false\n"
        "ROUTE 0 0\n"
        "ROUTE 0 0\n"
        "ROUTE 0 0"
    )
    res3 = sol.solveRequestRoutingSystem(input_str_3)
    print("Example 3:", res3)
    # Expected: ["OK", "OK", "OK", "OK", "node-A 0 node-A,node-B", "node-B 0 node-A,node-B", "None node-A,node-B"]