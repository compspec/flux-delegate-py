##############################################################
# Copyright 2023 Lawrence Livermore National Security, LLC
# (c.f. AUTHORS, NOTICE.LLNS, COPYING)
#
# This file is part of the Flux resource manager framework.
# For details, see https://github.com/flux-framework.
#
# SPDX-License-Identifier: LGPL-3.0
##############################################################

import logging
import sys
import argparse

import flux
import flux.cli.submit as base

LOGGER = logging.getLogger("flux-remote")


def open_logfile(fd):
    return open(fd, "w", encoding="utf8", errors="surrogateescape")


class SubmitCmd(base.SubmitCmd):
    def main(self, args):
        """
        Add a step before main to run feasibility check.

        The args have the job info we can further parse!
        """
        self.feasibility_check(args)
        self.submit_async_with_cc(args)
        self.run_and_exit()

    def feasibility_check(self, args):
        print("TODO VANESSA add fractale checks here.")


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
        parser.add_argument("command", help="Subcommand to run (e.g., 'submit')")

        # This just processes our added command (expecting other subcommands eventually)
        args, remaining_argv = parser.parse_known_args()

        # Now, we dispatch to the correct handler based on the command.
        if args.command == "submit":
            self.handle_submit(remaining_argv)

    def handle_submit(self, argv):
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

        sys.argv = ["flux", "submit"] + argv
        args = submit_parser.parse_args()
        args.func(args)


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
