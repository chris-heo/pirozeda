from __future__ import print_function
import time
import random
import math
import json

if __name__ == "__main__":
    outdata = {"time" : 0, "temperature" : [0] * 4, "output" : [0] * 3}


    timestamp = time.time()
    tstep = 120 # seconds
    tjitter = 0.200
    cnt = 2000

    print("[", end='')
    for i in range(cnt):
        timestamp += tstep + (random.random() * tjitter) - tjitter / 2
        outdata["time"] = timestamp

        outdata["temperature"][0] = (math.sin(timestamp / 86400 * 2 * math.pi) + 1) * 40 + 20 + math.sin(timestamp / 86400 / 10 * 2 * math.pi) * 10 + random.random() * 5
        outdata["temperature"][1] = (math.sin(timestamp / 86400 * 2 * math.pi + random.random()) + 1) * 40 + 22 + math.sin(timestamp / 86400 / 11 * 2 * math.pi) * 6
        outdata["temperature"][2] = outdata["temperature"][0] - outdata["temperature"][1] + 10 + random.random() * 5
        outdata["temperature"][3] = (outdata["temperature"][3] + outdata["temperature"][2]) / 2;

        outdata["output"][0] = min(max(0,outdata["temperature"][0] - 50) * 2, 100)


        
        print(json.dumps(outdata), end='')
        if i < (cnt - 1):
            print(", ", end='')
    print("]", end='')
    
            

