import os
import sys

def handle_delegation(jobid, uri):
    """
    This function is called from the C plugin.
    It receives the jobid and the remote URI.
    """
    # Log to a file for debugging, since stdout/stderr can be tricky from C
    log_path = "/tmp/delegate_plugin.log"
    with open(log_path, "a") as f:
        f.write(f"Python handler called!\n")
        f.write(f"  Job ID: {jobid}\n")
        f.write(f"  URI: {uri}\n")
        f.write(f"  PID: {os.getpid()}\n")

    # TODO put flux.job.submit/wait logic here.
    # I'll write this in a bit - want to think about integration with fractale
    # For now just return 0 for success!
    return 0
