import subprocess

from gonjacutils import get_random_id
class GonjacBuilder(object):
    def __init__(self, repo_name, branch, flags=""):
        self.build_id = get_random_id()
        self.repo_name = repo_name
        self.branch = branch
        self.flags = flags
        self.tar_name = "%s-%s-%s" %\
                (repo_name, branch, self.build_id)
    
    def start_job(self):
        cmd = "./gonjac-builder.sh -r %s -b %s -i %s" %\
                (self.repo_name, self.branch, self.build_id)
        print "Executing %s" % cmd
        ret_code = subprocess.call(cmd.split())
        if ret_code:
            return False
        else:
            return True
    
    
