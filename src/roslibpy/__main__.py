import json

import roslibpy


def rostopic_list(ros, **kwargs):
    for topic in ros.get_topics():
        print(topic)


def rostopic_type(ros, topic, **kwargs):
    topic_type = ros.get_topic_type(topic)
    print(topic_type)


def rostopic_find(ros, type, **kwargs):
    for topic in ros.get_topics_for_type(type):
        print(topic)


def rosmsg_info(ros, type, **kwargs):
    typedef = ros.get_message_details(type)
    _print_type(typedef)


def rosservice_list(ros, **kwargs):
    for service in ros.get_services():
        print(service)


def rosservice_type(ros, service, **kwargs):
    service_type = ros.get_service_type(service)
    print(service_type)


def rosservice_find(ros, type, **kwargs):
    for service in ros.get_services_for_type(type):
        print(service)


def rossrv_info(ros, type, **kwargs):
    _print_type(ros.get_service_request_details(type))
    print('---')
    _print_type(ros.get_service_response_details(type))


def rosservice_info(ros, service, **kwargs):
    type_name = ros.get_service_type(service)

    print('Type: %s\n' % type_name)
    print('Message definition')
    print('------------------')

    rossrv_info(ros, type_name)


def rosparam_list(ros, **kwargs):
    for param in ros.get_params():
        print(param)


def rosparam_set(ros, param, value, **kwargs):
    ros.set_param(param, json.loads(value))


def rosparam_get(ros, param, **kwargs):
    print(ros.get_param(param))


def rosparam_delete(ros, param, **kwargs):
    ros.delete_param(param)


def _print_typedef(typedef, def_map, level):
    defs = def_map[typedef]
    for fname, ftype, flen in zip(defs['fieldnames'], defs['fieldtypes'], defs['fieldarraylen']):
        if flen == -1:
            ftype_info = ftype
        elif flen == 0:
            ftype_info = ftype + '[]'
        else:
            ftype_info = '%s[%d]' % (ftype, flen)

        print('%s%s %s' % ('  ' * level, ftype_info, fname))
        if ftype in def_map:
            _print_typedef(ftype, def_map, level + 1)


def _print_type(typedata):
    if len(typedata['typedefs']) == 0:
        return

    main_type = typedata['typedefs'][0]['type']
    def_map = {typedef['type']: typedef for typedef in typedata['typedefs']}
    _print_typedef(main_type, def_map, 0)


def main():
    import argparse

    parser = argparse.ArgumentParser(description='roslibpy command-line utility')
    parser.add_argument('-r', '--ros-host', type=str, help='ROS host name or IP address', default='localhost')
    parser.add_argument('-p', '--ros-port', type=int, help='ROS bridge port', default=9090)

    commands = parser.add_subparsers(help='commands')
    commands.dest = 'command'
    commands.required = True

    # Command: topic
    topic_command = commands.add_parser('topic', help='ROS Topics')
    topic_subcommands = topic_command.add_subparsers(help='ROS topic commands')
    topic_subcommands.dest = 'subcommand'
    topic_subcommands.required = True

    topic_list_parser = topic_subcommands.add_parser('list', help='List available ROS topics')
    topic_list_parser.set_defaults(func=rostopic_list)

    topic_type_parser = topic_subcommands.add_parser('type', help='ROS topic type')
    topic_type_parser.add_argument('topic', action='store', type=str, help='Topic name')
    topic_type_parser.set_defaults(func=rostopic_type)

    topic_find_parser = topic_subcommands.add_parser('find', help='ROS topics by type')
    topic_find_parser.add_argument('type', action='store', type=str, help='Type name')
    topic_find_parser.set_defaults(func=rostopic_find)

    # Command: msg
    msg_command = commands.add_parser('msg', help='ROS Message type information')
    msg_subcommands = msg_command.add_subparsers(help='ROS Message type commands')
    msg_subcommands.dest = 'subcommand'
    msg_subcommands.required = True

    msg_info_parser = msg_subcommands.add_parser('info', help='ROS message type information')
    msg_info_parser.add_argument('type', action='store', type=str, help='Message type')
    msg_info_parser.set_defaults(func=rosmsg_info)

    # Command: service
    service_command = commands.add_parser('service', help='ROS Services')
    service_subcommands = service_command.add_subparsers(help='ROS service commands')
    service_subcommands.dest = 'subcommand'
    service_subcommands.required = True

    service_list_parser = service_subcommands.add_parser('list', help='List available ROS services')
    service_list_parser.set_defaults(func=rosservice_list)

    service_type_parser = service_subcommands.add_parser('type', help='ROS service type')
    service_type_parser.add_argument('service', action='store', type=str, help='Service name')
    service_type_parser.set_defaults(func=rosservice_type)

    service_find_parser = service_subcommands.add_parser('find', help='ROS services by type')
    service_find_parser.add_argument('type', action='store', type=str, help='Type name')
    service_find_parser.set_defaults(func=rosservice_find)

    service_info_parser = service_subcommands.add_parser('info', help='ROS service information')
    service_info_parser.add_argument('service', action='store', type=str, help='Service name')
    service_info_parser.set_defaults(func=rosservice_info)

    # Command: srv
    srv_command = commands.add_parser('srv', help='ROS Service type information')
    srv_subcommands = srv_command.add_subparsers(help='ROS service type commands')
    srv_subcommands.dest = 'subcommand'
    srv_subcommands.required = True

    srv_info_parser = srv_subcommands.add_parser('info', help='ROS service type information')
    srv_info_parser.add_argument('type', action='store', type=str, help='Service type')
    srv_info_parser.set_defaults(func=rossrv_info)

    # Command: param
    param_command = commands.add_parser('param', help='ROS Params')
    param_subcommands = param_command.add_subparsers(help='ROS parameter commands')
    param_subcommands.dest = 'subcommand'
    param_subcommands.required = True

    param_list_parser = param_subcommands.add_parser('list', help='List available ROS parameters')
    param_list_parser.set_defaults(func=rosparam_list)

    param_set_parser = param_subcommands.add_parser('set', help='Set ROS param value')
    param_set_parser.add_argument('param', action='store', type=str, help='Param name')
    param_set_parser.add_argument('value', action='store', type=str, help='Param value')
    param_set_parser.set_defaults(func=rosparam_set)

    param_get_parser = param_subcommands.add_parser('get', help='Get ROS param value')
    param_get_parser.add_argument('param', action='store', type=str, help='Param name')
    param_get_parser.set_defaults(func=rosparam_get)

    param_delete_parser = param_subcommands.add_parser('delete', help='Delete ROS param')
    param_delete_parser.add_argument('param', action='store', type=str, help='Param name')
    param_delete_parser.set_defaults(func=rosparam_delete)

    # Invoke
    args = parser.parse_args()
    ros = roslibpy.Ros(args.ros_host, args.ros_port)

    try:
        ros.run()
        args.func(ros, **vars(args))
    finally:
        ros.terminate()


if __name__ == '__main__':
    main()
