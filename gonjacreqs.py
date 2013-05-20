GENERIC_KEY_TYPE = "type"
GENERIC_KEY_IP = "ip"
GENERIC_KEY_PLATFORM = "platform"
GENERIC_KEY_TESTCONN = "testconn"
GENERIC_JOBDONE = "jobdone"
GENERIC_BUILD_ID = "buildid"
GENERIC_BRANCH = "branch"
GENERIC_REPO = "repo"
GENERIC_FLAGS = "flags"
GENERIC_URL = "url"

LOCAL_REGISTER = "register"
LOCAL_UNREGISTER = "unregister"
LOCAL_TESTCONN = "testconn"

REMOTE_REGACK = "regack"
REMOTE_NEWJOB = "newjob"
REMOTE_JOBSTART = "jobstart"
REMOTE_TESTCONNDENY = "testconndeny"
REMOTE_TESTCONNACK = "testconnack"

VALID_LOCAL_REQ_KEYS=[GENERIC_KEY_TYPE,
                      GENERIC_KEY_IP,
                      GENERIC_KEY_PLATFORM]

VALID_LOCAL_REQ_TYPES=[LOCAL_REGISTER,
                       LOCAL_UNREGISTER,
                       LOCAL_TESTCONN]

VALID_REMOTE_REQ_KEYS=[GENERIC_KEY_TYPE,
                       GENERIC_BRANCH,
                       GENERIC_REPO,
                       GENERIC_FLAGS,
                       GENERIC_BUILD_ID,
                       GENERIC_URL]

VALID_REMOTE_REQ_TYPES=[REMOTE_REGACK,
                        REMOTE_NEWJOB,
                        REMOTE_TESTCONNDENY,
                        REMOTE_TESTCONNACK]