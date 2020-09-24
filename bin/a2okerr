#!/usr/bin/env python3

import a2conf
import argparse
import socket
import os
import okerrupdate

project = okerrupdate.OkerrProject()


def process_file(path, args):
    root = a2conf.Node(name='#root', includes=args.includes)
    root.read_file(path)

    for vhost in root.children('<VirtualHost>'):
        try:
            servername = next(vhost.children('servername')).args
        except StopIteration:
            print("WARNING skip vhost {} ({}) in file {} because no ServerName".format(vhost, vhost.args, path))
            continue

        try:
            sslengine = next(vhost.children('sslengine'))
        except StopIteration:
            continue
        if sslengine.args.lower() != 'on':
            continue

        iname = args.prefix + servername
        i = project.indicator(iname,
                              method='sslcert|host={}|port=443|days=20'.format(servername),
                              policy=args.policy,
                              desc=args.desc)
        if args.dry:
            print(i, '(dry run)')
        else:
            print(i)

        if not args.dry:
            try:
                i.update('OK')
            except okerrupdate.OkerrExc as e:
                if e.code == 'BAD_METHOD':
                    print("Already exists")
                else:
                    print(e)


def main():

    def_prefix = socket.gethostname().split('.')[0]+':ssl:https:'
    def_file = '/etc/apache2/apache2.conf'
    def_dir = None
    def_policy = 'Daily'
    def_desc = 'Auto-created from a2conf a2okerr.py'

    parser = argparse.ArgumentParser(description='Bulk-add Apache2 SSL hosts to Okerr monitoring')


    parser.add_argument(dest='file', nargs='?', default=def_file, metavar='PATH',
                        help='Config file(s) path (def: {}). Either filename or directory'.format(def_file))

    parser.add_argument('-d', '--dir', default=def_dir, metavar='DIR_PATH',
                        help='Process all files files in directory (e.g. /etc/apache2/sites-enabled/). def: None'.format(def_dir))
    parser.add_argument('--prefix', default=def_prefix, metavar='PATH',
                        help='prefix (def: {})'.format(def_prefix))
    parser.add_argument('--policy', default=def_policy, metavar='Policy',
                        help='okerr policy (def: {})'.format(def_policy))
    parser.add_argument('--desc', default=def_desc, metavar='DESC',
                        help='description (def: {})'.format(def_desc))
    parser.add_argument('--dry', default=False, action='store_true',
                        help='dry run, do not update anything')
    parser.add_argument('-v', dest='verbose', action='store_true',
                        default=False, help='verbose mode')
    parser.add_argument('--no-includes', default=True, dest='includes', action='store_false',
                        help='Disable processing Include* directives')

    args = parser.parse_args()

    if os.path.isdir(args.file):
        for f in os.listdir(args.file):
            path = os.path.join(args.file, f)
            if not (os.path.isfile(path) or os.path.islink(path)):
                continue
            process_file(path, args)
    else:
        process_file(args.file, args)


main()
