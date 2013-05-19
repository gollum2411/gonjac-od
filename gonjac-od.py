#!/usr/bin/env python

import optparse
import sys
import os

import gonjacserver
import gonjaccore
import gonjacutils
import gonjacerrors

if __name__ == '__main__':
    parser = optparse.OptionParser()
    parser.add_option("--startserver", dest="do_start",
                      help="Start server", action="store_true")
    parser.add_option("--stopserver", dest="do_stop",
                      help="Stop server", action="store_true")
    parser.add_option("--register", dest="register_ip",
                      help="Register with master server",
                      action="store")
    parser.add_option("--autoregister", dest="autoreg",
                      help="Use remote IP from gonjac.config",
                      action="store_true")
    parser.add_option("--unregister", dest="do_unregister",
                     help="Unregister from master server",
                     action="store_true")
    parser.add_option("--testconn", dest="test_conn",
                      help="Test if a session has been established with\
                            the master server",
                      action="store_true")
    opts, args = parser.parse_args()
    
    if opts.do_start and opts.do_stop:
        sys.stderr.write("Either start or stop server, not both!\n")
        sys.exit(-1)
    
    if opts.do_start:
        gonjacserver.init_gonjac_server()
                
    if opts.do_stop:
        gonjacserver.stop_gonjac_server()
        
    if opts.register_ip:
        if gonjacserver.is_gonjac_server_running():
            if gonjacserver.do_register(opts.register_ip):
                sys.stdout.write(gonjacerrors.REGISTER_SUCCESS)
            else:
                sys.stdout.write(gonjacerrors.REGISTER_FAILED)
        else:
            sys.stderr.write(gonjacerrors.SERVER_NOT_RUNNING)
            sys.exit(-1)
    
    if opts.autoreg:
        ip = gonjacutils.GonjacConfig.get_remote_ip()
        if gonjacutils.is_valid_ip(ip):
            gonjacserver.do_register(ip)
        else:
            sys.stderr.write(gonjacerrors.DO_REGISTER)
    
    if opts.do_unregister:
        if gonjacserver.is_gonjac_server_running():
            gonjacserver.do_unregister()
        else:
            sys.stderr.write(gonjacerrors.SERVER_NOT_RUNNING)
            sys.exit(-1)
    
    if opts.test_conn:
        if gonjacserver.is_gonjac_server_running():
            if gonjacserver.do_testconn():
                sys.stdout.write(gonjacerrors.SESSION_ESTABLISHED)
            else:
                sys.stdout.write(gonjacerrors.SESSION_FAILED)
        else:
            sys.stderr.write(gonjacerrors.SERVER_NOT_RUNNING)
        