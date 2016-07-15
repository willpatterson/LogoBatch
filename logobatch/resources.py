""" For classes managing computing and storage resources """

import os
import sys

class compute_resource(object):
    def __init__(self, name, hostname):
        self.name = name
        self.hostname = name

    def run_jobs(self):
        """ """
        raise NotImplementedError

