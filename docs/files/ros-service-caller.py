import roslibpy

client = roslibpy.Ros(host='localhost', port=9090)
client.run()
client.on_ready(lambda: call_service())

service = roslibpy.Service(client, '/rosout/get_loggers', 'roscpp/GetLoggers')


def call_service():
    print('Calling service')
    request = roslibpy.ServiceRequest()
    service.call(request, success_callback, error_callback)


def success_callback(result):
    print('Service response: ', result['loggers'])


def error_callback(result):
    print('Something went wrong')


try:
    while True:
        pass
except KeyboardInterrupt:
    pass

client.terminate()
