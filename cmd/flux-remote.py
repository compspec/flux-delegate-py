##############################################################
# Copyright 2023 Lawrence Livermore National Security, LLC
# (c.f. AUTHORS, NOTICE.LLNS, COPYING)
#
# This file is part of the Flux resource manager framework.
# For details, see https://github.com/flux-framework.
#
# SPDX-License-Identifier: LGPL-3.0
##############################################################

import argparse
import logging
import os
import sys
import tempfile

import flux
import flux.cli.submit as base
import fractale.defaults as defaults
import fractale.utils as utils
from compspec.plugin.registry import PluginRegistry
from fractale.store import FractaleStore
from fractale.subsystem import get_subsystem_solver

registry = PluginRegistry()
registry.discover()

LOGGER = logging.getLogger("flux-remote")


def open_logfile(fd):
    return open(fd, "w", encoding="utf8", errors="surrogateescape")


class SubmitCmd(base.SubmitCmd):
    def main(self, args, remote_args, dry_run=False):
        """
        Add a step before main to run feasibility check.

        The args have the job info we can further parse!
        """
        # Feasibility check handles args from flux remote
        with_delegation = self.feasibility_check(args, remote_args)
        if dry_run:
            sys.exit(0)

        # Submit the jobspec args, which may now have delegation
        self.submit_async_with_cc(with_delegation)
        self.run_and_exit()

    def feasibility_check(self, args, remote_args):
        """
        Check feasibility based on local user subsystems with fractale library.
        """
        jobspec = self.jobspec_create(args)
        store = FractaleStore(remote_args.config_dir)

        # Detect or discover local cluster resources if no store created
        if not os.path.exists(store.root):
            store.detect()

        # If we detect and none still found, there are none.
        if not os.path.exists(store.root):
            sys.exit("No subsystems found.")

        # TODO Vanessa - this is parsing the wrong format. I need to update it.
        # I want to make a hardened organization for this. Operations across clusters can be in in parallel
        # ----
        # 1. Each detected cluster needs a remote URI or credential (e.g., Kubernetes)
        #   - TODO: we should be able to detect kubernetes cluster as ephemeral
        #   - TODO: make compspec-kube for this use case.
        # 2. For feasibility, we first check cluster resources for each known cluster
        # 3. We then check subsystem requests that come from requires (e.g. --setattr=requires.software=spack:curl)
        # 4. Based on the filtered set:
        #    - For Flux we finalize, add the delegation plugin URI, and we are done.
        #    - For Kubernetes, it's easier (an API call) and this should also be done by delegation
        # 5. Fall through case (no remote matches) we submit as usual to local cluster instance
        solver = get_subsystem_solver(store.clusters_root, remote_args.solver)
        is_satisfied = solver.satisfied(jobspec.jobspec)

        # If we are satisifed, we can get the result, and then add it to the JobSpec as a delegate dependency. We will
        # That would look like this:
        # args.setattr = [f'delegate.local_uri=${uri}']
        return args


class RemoteSubmitCmd(base.SubmitCmd):
    """
    RemoteSubmitCmd submits a job, displays the jobid on stdout, and returns.
    We extend SubmitCmd from the base class to handle doing a local feasibility
    check first. We do this before we send to flux (and JobTap) so we do not
    unecessarily send to a cluster that is not already checked.

    Usage: flux remote submit [OPTIONS] cmd ...
    """

    def run_parser(self):
        """
        The main remote parser is very simple. It only looks for the subcommand.
        """
        parser = argparse.ArgumentParser(
            prog="flux remote",
            description="A command to interact with a remote Flux instance.",
            usage="flux remote <command> [options...]",
        )
        # Let's not require graph_tool to start, make default database
        # I don't think we can assume everything is structed like a graph
        parser.add_argument(
            "--solver",
            help="subsystem solved backend",
            default="database",
            choices=defaults.solver_backends,
        )
        parser.add_argument(
            "--config-dir",
            dest="config_dir",
            help="Fractale configuration directory to store subsystems. Defaults to ~/.fractale",
        )
        # IMPORTANT: if you add more args here, submit will stop working, and you need
        # to account for parsing them out.
        parser.add_argument("command", help="Subcommand to run (e.g., 'submit')")

        # This just processes our added command (expecting other subcommands eventually)
        args, remaining_argv = parser.parse_known_args()

        # Now, we dispatch to the correct handler based on the command.
        if args.command == "submit":
            self.handle_submit(remaining_argv, args, dry_run="--dry-run" in sys.argv)
        else:
            print(
                f"{args.command} is not a recognized Flux command. Try `flux remote submit`"
            )

    def handle_submit(self, argv, remote_args, dry_run=False):
        """
        Handle the submit subcommand.

        We need special parsing for help.
        """
        submit = SubmitCmd("flux submit", description="enqueue a job")
        submit_parser = submit.get_parser()
        submit_parser.set_defaults(func=submit.main)

        # We need to handle this manually since it's off base for argparse
        if "-h" in argv or "--help" in argv:
            submit.parser.print_help()
            sys.exit(0)

        # Repopulate the initial submit args
        sys.argv = argv
        args = submit_parser.parse_args()
        args.func(args, remote_args, dry_run)


@flux.util.CLIMain(LOGGER)
def main():
    sys.stdout = open_logfile(sys.stdout.fileno())
    sys.stderr = open_logfile(sys.stderr.fileno())

    # This is going to be a submit parser with extra bells and whistles
    submit = RemoteSubmitCmd(
        "flux remote", description="enqueue a multi-cluster (including remote) job"
    )
    submit.run_parser()


if __name__ == "__main__":
    main()
