"""
Checks the health of the system.
"""

from global_variables import gv
from job_tracker import JobTracker

if __name__ == '__main__':

    # check health of the system
    JobTracker(gv).check_health(gv)
