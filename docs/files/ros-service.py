import roslibpy

def handler(request, response):
    print('Setting speed to {}'.format(request['data']))
    response['success'] = True
    return True

client = roslibpy.Ros(host='localhost', port=9090)

service = roslibpy.Service(client, '/set_ludicrous_speed', 'std_srvs/SetBool')
service.advertise(handler)
print('Service advertised.')

client.run_forever()
client.terminate()
