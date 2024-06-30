from __future__ import print_function
import roslibpy

client = roslibpy.Ros(host='localhost', port=9090)
client.run()

action_client = roslibpy.ActionClient(client,
                                      '/fibonacci',
                                      'custom_action_interfaces/action/Fibonacci')

def result_callback(msg):
    print('Action result:',msg['sequence'])

def feedback_callback(msg):
    print('Action feedback:',msg['partial_sequence'])

def fail_callback(msg):
    print('Action failed:',msg)

goal_id = action_client.send_goal(roslibpy.ActionGoal({'order': 8}),
                                  result_callback,
                                  feedback_callback,
                                  fail_callback)

goal.on('feedback', lambda f: print(f['sequence']))
goal.send()
result = goal.wait(10)
action_client.dispose()

print('Result: {}'.format(result['sequence']))
