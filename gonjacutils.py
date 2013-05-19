import os
import sys
import re
import ConfigParser

import gonjacerrors

try:
    import psutil
except Exception:
    sys.stderr.write(gonjacerrors.INSTALL_PSUTIL)
    sys.exit(-1)

import gonjacserver
import gonjaccore
import gonjacreqs

class GonjacConfig(object):
    confpath = gonjaccore.CONF
    remote_ip = None
    sysinfo = None
    conf = None
    
    @classmethod
    def read(cls):
        cls.conf = ConfigParser.ConfigParser()
        cls.conf.read(cls.confpath)
        cls.remote_ip = cls.conf.get("remote", "ip")
        cls.sysinfo = cls.conf.get("sysinfo", "platform")
    
    @classmethod
    def set_remote_ip(cls, ip):
        if not cls.conf:
            cls.read()
        cls.conf.set("remote", "ip", ip)
        cls.conf.write(open(gonjaccore.CONF, 'w'))
        cls.read()
    
    @classmethod
    def get_remote_ip(cls):
        if not cls.conf:
            cls.read()
        return cls.conf.get("remote", "ip").strip('"')
    
    @classmethod
    def get_platform(cls):
        if not cls.conf:
            cls.read()
        return cls.conf.get("sysinfo", "platform").strip('"')

def is_valid_ip(str_ip):
    if re.match(gonjaccore.IP_REGEX, str_ip):
        return True
    else:
        return False    

def get_new_config():
    try:
        os.remove(gonjaccore.CONF)
    except IOException:
        pass
    
    return dict()

def get_config():
    config = ConfigParser.ConfigParser()
    config.read(gonjaccore.CONF)
    return config

def set_config_opt(config, section, key, value):
    config.set(section, key, value)

def flush_config():
    pass

def is_req_regack(req):
    if req.type == gonjacreqs.REMOTE_REGACK:
        return True
    else:
        return False

def validate_local_keys(req):
    for k in req.get_dict().keys():
        if k not in gonjacreqs.VALID_LOCAL_REQ_KEYS:
            raise ValueError("Invalid local request key: %s" % k)
    
def validate_local_type(req):
    if not req.type in gonjacreqs.VALID_LOCAL_REQ_TYPES:
        raise ValueError("Invalid local request type: %s" % req.type)

def validate_register(req):
    if not req[gonjacreqs.GENERIC_KEY_IP]:
        req[gonjacreqs.GENERIC_KEY_IP] = \
            GonjacConfig.get_remote_ip()
    
    if not req[gonjacreqs.GENERIC_KEY_PLATFORM]:
        req[gonjacreqs.GENERIC_KEY_PLATFORM] = \
            GonjacConfig.get_platform()

def validate_unregister(req):
    if not req[gonjacreqs.GENERIC_KEY_IP]:
        req[gonjacreqs.GENERIC_KEY_IP] = \
            GonjacConfig.get_remote_ip()

def validate_testconn(req):
    if not req[gonjacreqs.GENERIC_KEY_IP]:
        req[gonjacreqs.GENERIC_KEY_IP] = \
            GonjacConfig.get_remote_ip()

def validate_remote_keys(req, remote_client):
    for k in req.get_dict().keys():
        if k not in gonjacreqs.VALID_REMOTE_REQ_KEYS:
            errstring = "Invalid remote request key: %s" % k
            remote_client.send(errstring)
            raise ValueError(errstring)

def validate_remote_type(req, remote_client):
    errstring = "Invalid remote request type: %s" % req.type
    if not req.type in gonjacreqs.VALID_REMOTE_REQ_TYPES:
        if remote_client:
            remote_client.send(errstring)
        raise ValueError(errstring)

def validate_remote_newjob(req, remote_client):
    if not req[gonjacreqs.REMOTE_REPO]:
        remote_client.send("No repo specified")
    if not req[gonjacreqs.REMOTE_BRANCH]:
        remote_client.send("No branch specified")
        raise ValueError("No branch specified")
    

