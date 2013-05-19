GENERIC_KEY_TYPE = "type"
GENERIC_KEY_IP = "ip"
GENERIC_KEY_PLATFORM = "platform"
GENERIC_KEY_TESTCONN = "testconn"

LOCAL_REGISTER = "register"
LOCAL_UNREGISTER = "unregister"
LOCAL_TESTCONN = "testconn"

REMOTE_REGACK = "regack"
REMOTE_NEWJOB = "newjob"
REMOTE_BRANCH = "branch"
REMOTE_REPO = "repo"
REMOTE_FLAGS = "flags"
REMOTE_TESTCONNDENY = "testconndeny"
REMOTE_TESTCONNACK = "testconnack"

VALID_LOCAL_REQ_KEYS=[GENERIC_KEY_TYPE,
                      GENERIC_KEY_IP,
                      GENERIC_KEY_PLATFORM]

VALID_LOCAL_REQ_TYPES=[LOCAL_REGISTER,
                       LOCAL_UNREGISTER,
                       LOCAL_TESTCONN]

VALID_REMOTE_REQ_KEYS=[GENERIC_KEY_TYPE]

VALID_REMOTE_REQ_TYPES=[REMOTE_REGACK,
                        REMOTE_NEWJOB,
                        REMOTE_REPO,
                        REMOTE_TESTCONNDENY,
                        REMOTE_TESTCONNACK]