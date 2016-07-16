""" For classes managing computing and storage resources """

import os
import sys

class resource(object):
    def __init__(self, name):
        self.name = name

class remote_compute(resource):
    def __init__(self, name, hostname):
        super.__init__(self, name)
        self.hostname = hostname

class local_storage(resource):
    def __init__(self, name, hostname, default_path=None):
        self.name = name
        self.hostname = name
        self.default_path = default_path

class remote_compute(remote_resource):
    def __init__(self, name, hostname):
        self.
        self.remote_storage = None
        self.fast_storage = None

    def run_jobs(self):
        """ """
        raise NotImplementedError

class local_compute(compute_resource):
    pass

class compute_server(compute_resource):
    pass

class compute_cluster(compute_resource):
    pass

class slurm_cluster(compute_cluster):
    pass

class sge_cluster(compute_cluster):
    pass
