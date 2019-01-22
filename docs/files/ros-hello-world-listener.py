import roslibpy

client = roslibpy.Ros(host='localhost', port=9090)
listener = roslibpy.Topic(client, '/chatter', 'std_msgs/String')


def start_listening():
    listener.subscribe(receive_message)

def receive_message(message):
    print('Heard talking: ' + message['data'])

client.on_ready(start_listening)
client.run_forever()
