import SocketServer
import socket
import os
import sys
import ast
import re
import threading
import signal
import copy

import gonjaccore
import gonjacreqs
import gonjacutils
import gonjacerrors

try:
    import psutil
except Exception:
    sys.stderr.write(gonjacerrors.INSTALL_PSUTIL)

GONJAC_PORT = 6666
LOCALHOST = "127.0.0.1"

class GonjacBaseRequest(object):
    """Base class container for requests.
    
    After setting key-value pairs, use validate_req()
    to make sure request is consistent, so as to avoid
    server-side issues.
    
    req_type : The type of the request
    a_dict : Optional initializer 
    
    """
    def __init__(self, req_type, a_dict=None):
        self._dict = dict()
        self._dict["type"] = req_type
        self.type = req_type
        
        if a_dict:
            for k, v in a_dict.iteritems():
                self._dict[k] = v
    
    def __getitem__(self, key):
        if self._dict.has_key(key):
            return self._dict[key]
        else:
            return None
    
    def __setitem__(self, key, item):
        self._dict[key] = item
        
    def __str__(self):
        return self._dict.__str__()
    
    def __getattribute__(self, name):
        if not hasattr(self, name):
            return None
        else:
            return object.__getattribute__(self, name)
    
    def __str__(self):
        ret_dict = copy.copy(self._dict)
        if ret_dict.has_key("_dict"):
            del ret_dict["_dict"]
        return "%s" % ret_dict
        
    def iteritems(self):
        for k, v in self._dict.iteritems():
            yield k, v
    
    def to_str(self):
        return self.__str__()
    
    def get_dict(self):
        ret_dict = copy.copy(self.__dict__)
        if ret_dict.has_key("_dict"):
            del ret_dict["_dict"]
        return ret_dict

class GonjacLocalRequest(GonjacBaseRequest):
    def __init__(self, req_type, req=None):
        GonjacBaseRequest.__init__(self, req_type, req)
        
class GonjacRemoteRequest(GonjacBaseRequest):
    def __init__(self, req_type, req=None):
        GonjacBaseRequest.__init__(self, req_type, req)

class GonjacHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        data = "dummy"
        while data:
            data = self.request.recv(2048)
            if not data:
                return
            try:
                req = self.parse_request(data)
            except gonjaccore.GonjacException as e:
                print e
                self.request.send(gonjacerrors.INVALID_REQUEST)
                continue
            
            request_ip, port = self.client_address
            
            if request_ip == LOCALHOST:
                #Pass the parsed dict to replicate the request as
                #a GonjacLocalRequest
                local_req = GonjacLocalRequest(req["type"], req)
                validate_req(local_req)
                print "Request from localhost"
                for k, v in local_req.iteritems():
                    print "\t%s : %s" % (k ,v)
                self.execute_local_req(local_req)
            elif request_ip == gonjacutils.GonjacConfig.get_remote_ip():
                print "Request from master server:,", str(req)
                remote_req = GonjacRemoteRequest(req["type"], req)
                validate_req(remote_req, self.request)
            else:
                self.request.send("Permission denied for host %s" % request_ip)
            
    def parse_request(self, reqstr):
        """Parse data from request, and attempt to parse as a dict."""
        try:
            obj = ast.literal_eval(reqstr)
        except (SyntaxError, ValueError):
            raise gonjaccore.GonjacException(gonjacerrors.UNRECOGNIZED_REQ)
        
        if type(obj) is dict:
            return obj
        else:
            raise gonjaccore.GonjacException(gonjacerrors.UNRECOGNIZED_REQ)
    
    def execute_local_req(self, local_request):
        if local_request.type == gonjacreqs.LOCAL_REGISTER:
            gonjacutils.GonjacConfig.set_remote_ip(
                local_request[gonjacreqs.GENERIC_KEY_IP]
                )
            sock = get_simple_client()
            sock.connect((local_request[gonjacreqs.GENERIC_KEY_IP],
                          GONJAC_PORT))
            sock.send(local_request.to_str())
            reqdict = self.parse_request(sock.recv(2048))
            remote_req = GonjacRemoteRequest(
                         reqdict[gonjacreqs.GENERIC_KEY_TYPE],
                         reqdict)
            if not gonjacutils.is_req_regack(remote_req):
                sock.send(gonjacerrors.INVALID_RESPONSE)
                do_unregister()
                self.request.send("fail")
            else:
                sock.close()
                #Set 
                gonjacutils.GonjacConfig.set_remote_ip(
                    local_request[gonjacreqs.GENERIC_KEY_IP]
                )
                self.request.send("pass")
            
        elif local_request.type == gonjacreqs.LOCAL_UNREGISTER:
            sock = get_simple_client()
            sock.connect((local_request[gonjacreqs.GENERIC_KEY_IP],
                         GONJAC_PORT))
            sock.send(local_request.to_str())
            sock.close()
        elif local_request.type == gonjacreqs.LOCAL_TESTCONN:
            sock = get_simple_client()
            sock.connect((local_request[gonjacreqs.GENERIC_KEY_IP],
                         GONJAC_PORT))
            sock.send(local_request.to_str())
            reqdict = self.parse_request(sock.recv(2024))
            req = GonjacRemoteRequest(
                reqdict[gonjacreqs.GENERIC_KEY_TYPE],
                reqdict)
            if req.type == gonjacreqs.REMOTE_TESTCONNACK:
                self.request.send("pass")
            elif req.type == gonjacreqs.REMOTE_TESTCONNDENY:
                self.request.send("fail")
            
    
            
class GonjacServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    def __init__(self, server_info, handler, autobind=True):
        SocketServer.TCPServer.__init__(self, server_info, handler, autobind)
        self.allow_reuse_address = True
        #Check if a remote ip has been configured before
        remote_ip = gonjacutils.GonjacConfig().get_remote_ip()
        if not gonjacutils.is_valid_ip(remote_ip):
            sys.stderr.write(gonjacerrors.DO_REGISTER)
    
def get_simple_client():
    return socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
def init_gonjac_server():
    child_pid = os.fork()
    if child_pid == 0:
        try:
            local_server_info = ("0.0.0.0", GONJAC_PORT)
            local_server = GonjacServer(local_server_info,
                                        GonjacHandler, False)
            local_server.allow_reuse_address = True
            local_server.timeout = 5
            local_server.server_bind()
            local_server.server_activate()
            print "Server listening on port %d" % GONJAC_PORT
            local_server.serve_forever()
        except socket.error, (value, message):
            sys.stderr.write(gonjacerrors.SERVER_ALREADY_RUNNING)
            sys.exit(-1)
    
    os.wait()
        
def stop_gonjac_server():
    for proc in psutil.process_iter():
        if proc.cmdline:
            cmd = reduce(lambda string, item: string + item, proc.cmdline, " ")
            if "gonjac" in cmd and "--startserver" in cmd:
                proc.kill()
                return
    sys.stderr.write(gonjacerrors.SERVER_NOT_RUNNING)
    sys.exit(0)
    
def is_gonjac_server_running():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind((LOCALHOST,
                   GONJAC_PORT))
        sock.close()
        return False
    except socket.error:
        return True
        
def do_register(server_ip):
    if not gonjacutils.is_valid_ip(server_ip):
        raise ValueError("Invalid IP")
    
    sock = get_simple_client()
    req = GonjacLocalRequest(gonjacreqs.LOCAL_REGISTER)
    req[gonjacreqs.GENERIC_KEY_IP] = server_ip
    sock.connect((LOCALHOST, GONJAC_PORT))
    sock.send(req.to_str())
    data = sock.recv(2048)
    if data == "pass":
        return True
    elif data == "fail":
        return False
    else:
        return False
    sock.close()

def do_unregister():
    old_ip = gonjacutils.GonjacConfig.get_remote_ip()
    if gonjacutils.is_valid_ip(old_ip):
        req = GonjacLocalRequest(gonjacreqs.LOCAL_UNREGISTER)
        sock = get_simple_client()
        sock.connect((LOCALHOST, GONJAC_PORT))
        sock.send(req.to_str())
        sock.close()
    else:
        sys.stderr.write(gonjacerrors.DO_REGISTER)
    
    gonjacutils.GonjacConfig.set_remote_ip("None")

def do_testconn():
    config = gonjacutils.GonjacConfig()
    config.read()
    remote_ip = config.get_remote_ip()
    if gonjacutils.is_valid_ip(remote_ip):
        req = GonjacLocalRequest(gonjacreqs.GENERIC_KEY_TESTCONN)
        sock = get_simple_client()
        sock.connect((LOCALHOST, GONJAC_PORT))
        sock.send(req.to_str())
        data = sock.recv(2048)
        if data == "pass":
            return True
        elif data == "fail":
            return False
        else:
            return False
        sock.close()
    else:
        sys.stderr.write(gonjacerrors.DO_REGISTER)
        sys.exit(-1)

def validate_req(gjreq, remote_client=None):
    """Validate consistency of a GonjacRequest instance."""
    if isinstance(gjreq, GonjacLocalRequest):
    #Check if all keys are permitted
        gonjacutils.validate_local_keys(gjreq)
        gonjacutils.validate_local_type(gjreq)
        if gjreq.type == gonjacreqs.LOCAL_REGISTER:
            gonjacutils.validate_register(gjreq)
        elif gjreq.type == gonjacreqs.LOCAL_UNREGISTER:
            gonjacutils.validate_unregister(gjreq)
        elif gjreq.type == gonjacreqs.GENERIC_KEY_TESTCONN:
            gonjacutils.validate_testconn(gjreq)
                
        #if gjreq.type == gonjacreqs.LOCAL_TESTCONN
    elif isinstance(gjreq, GonjacRemoteRequest):
        gonjacutils.validate_remote_keys(gjreq, remote_client)
        gonjacutils.validate_remote_type(gjreq, remote_client)
        # If request type is regack, nothing to be done
        if gjreq.type == gonjacreqs.REMOTE_REGACK:
            return
        if gjreq.type == gonjacreqs.REMOTE_NEWJOB:
            gonjacutils.validate_remote_newjob(gjreq, remote_client)
