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
import shutil
import sys
import tempfile
from datetime import datetime

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


class DetectCmd(base.SubmitCmd):
    def main(self, args):
        """
        Detect local subsystems.

        This doesn't technically need to be based on submit.
        """
        # If we are exporting, we are going to run detect in a non-existing directory
        cleanup = False
        if args.export and not args.config_dir:
            args.config_dir = tempfile.mkdtemp(prefix="flux-detect-")
            cleanup = True
        store = FractaleStore(args.config_dir)
        store.detect(force=args.force)

        # Export locally detected subsystems
        if args.export:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archive_name = f"fractale-export-{timestamp}"
            shutil.make_archive(archive_name, "zip", args.config_dir)

            # Cleanup if we created a temporary context
            if cleanup and os.path.exists(args.config_dir):
                shutil.rmtree(args.config_dir)

    def run_parser(self):
        """
        The main remote parser is very simple. It only looks for the subcommand.
        """
        parser = argparse.ArgumentParser(
            prog="flux detect",
            description="Detect and save local subsystem metadata.",
            usage="flux detect <command> [options...]",
        )
        parser.add_argument(
            "--config-dir",
            dest="config_dir",
            help="Fractale configuration directory to store subsystems. Defaults to ~/.fractale",
        )
        parser.add_argument(
            "--force",
            help="Given existing metadata, force an update.",
            action="store_true",
            default=False,
        )
        parser.add_argument(
            "--export",
            default=False,
            action="store_true",
            help="Export to local archive for later import.",
        )

        # We need to handle this manually since it's off base for argparse
        if "-h" in sys.argv or "--help" in sys.argv:
            parser.print_help()
            sys.exit(0)

        # This just processes our added command (expecting other subcommands eventually)
        args, extra = parser.parse_known_args()
        self.main(args)


@flux.util.CLIMain(LOGGER)
def main():
    sys.stdout = open_logfile(sys.stdout.fileno())
    sys.stderr = open_logfile(sys.stderr.fileno())

    # This is going to be a submit parser with extra bells and whistles
    detect = DetectCmd("flux detect", description="detect local subsystems")
    detect.run_parser()


if __name__ == "__main__":
    main()
