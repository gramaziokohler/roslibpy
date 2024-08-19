from __future__ import print_function
import roslibpy
import time


global result

client = roslibpy.Ros(host="localhost", port=9090)
client.run()

action_client = roslibpy.ActionClient(client,
                                      "/fibonacci",
                                      "custom_action_interfaces/action/Fibonacci")
result = None

def result_callback(msg):
    global result
    result = msg["result"]

def feedback_callback(msg):
    print(f"Action feedback: {msg['partial_sequence']}")

def fail_callback(msg):
    print(f"Action failed: {msg}")

goal_id = action_client.send_goal(roslibpy.ActionGoal({"order": 8}),
                                  result_callback,
                                  feedback_callback,
                                  fail_callback)

while result == None:
    time.sleep(1)
    
print("Action result: {}".format(result["sequence"]))
