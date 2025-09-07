AC_PREREQ([2.69])
AC_INIT([flux-delegate-plugin], [0.1.0], [user@example.com])
AC_CONFIG_MACRO_DIRS([m4])
AM_INIT_AUTOMAKE([-Wall -Werror foreign])
AC_CONFIG_SRCDIR([delegate_c_bridge.c])
AC_CONFIG_HEADERS([config.h])

# Checks for programs
AC_PROG_CC
AM_PROG_AR
LT_INIT

# Check for flux-core and substitute its variables
PKG_CHECK_MODULES([FLUX_CORE], [flux-core],, [AC_MSG_ERROR([flux-core not found])])
AC_SUBST([FLUX_CORE_CFLAGS])
AC_SUBST([FLUX_CORE_LIBS])

# Check for Python and substitute its variables
AC_PATH_PROG([PYTHON_CONFIG], [python3-config])
if test -z "$PYTHON_CONFIG"; then
    AC_MSG_ERROR([python3-config not found. Please install python3-dev or python3-devel.])
fi
PYTHON_CFLAGS=$($PYTHON_CONFIG --cflags)
PYTHON_LIBS=$($PYTHON_CONFIG --embed --ldflags)
AC_SUBST([PYTHON_CFLAGS])
AC_SUBST([PYTHON_LIBS])

AC_CONFIG_FILES([Makefile])
AC_OUTPUT