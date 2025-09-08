###########################################################################
# Build C Stuff Rules
###########################################################################

ACLOCAL_AMFLAGS = -I m4

pkglib_LTLIBRARIES = delegate_c_bridge.la

delegate_c_bridge_la_SOURCES = delegate_c_bridge.c

delegate_c_bridge_la_CFLAGS = @FLUX_CORE_CFLAGS@ @PYTHON_CFLAGS@

delegate_c_bridge_la_LDFLAGS = -module -avoid-version -shared -pthread

delegate_c_bridge_la_LIBADD = @FLUX_CORE_LIBS@ @PYTHON_LIBS@ -ldl

###########################################################################
# Install Script Rules
###########################################################################

# $(libexecdir) is a standard autotools thing (e.g., /usr/libexec).
fluxcmddir = $(libexecdir)/flux/cmd

# Using _SCRIPTS ensures the file is installed with execute permissions.
fluxcmd_SCRIPTS = cmd/flux-remote.py

clean-local:
	@echo "--- Running cleanup ---"
	rm -f configure aclocal.m4 Makefile.in config.h.in ltmain.sh
	rm -f compile depcomp install-sh missing
	rm -f ./config.guess ar-lib configure~ stamp-h1 config.sub
	rm -rf autom4te.cache/ build-aux/ m4/
	rm -f Makefile config.status config.log config.h libtool
	rm -rf __pycache__/
	@echo "--- Cleanup complete ---"
