#include <Python.h>
#include <flux/jobtap.h>
#include <jansson.h>
#include <dlfcn.h>
#include <string.h>
#include <pthread.h>
#include <stdlib.h>

typedef struct {
    long long jobid;
    char *remote_uri;
    char *jobspec_str;
    char *local_uri;
} thread_args_t;

// worker_thread handles the loading of Python, submit, etc.
void *worker_thread(void *arg) {
    thread_args_t *args = (thread_args_t *)arg;
    void *libpython_handle = NULL;
    PyObject *pName = NULL, *pModule = NULL, *pFunc = NULL, *pArgs = NULL, *pValue = NULL;

    libpython_handle = dlopen("libpython3.10.so", RTLD_LAZY | RTLD_GLOBAL);
    if (!libpython_handle) { goto cleanup; }
    Py_Initialize();
    PyRun_SimpleString("import sys; sys.path.append('.')");

    pName = PyUnicode_DecodeFSDefault("delegate_handler");
    pModule = PyImport_Import(pName); Py_XDECREF(pName);
    if (!pModule) { PyErr_Print(); goto cleanup; }

    pFunc = PyObject_GetAttrString(pModule, "handle_delegation");
    if (!pFunc || !PyCallable_Check(pFunc)) { PyErr_Print(); goto cleanup; }

    pArgs = PyTuple_New(4);
    PyTuple_SetItem(pArgs, 0, PyLong_FromLongLong(args->jobid));
    PyTuple_SetItem(pArgs, 1, PyUnicode_FromString(args->remote_uri));
    PyTuple_SetItem(pArgs, 2, PyUnicode_FromString(args->jobspec_str));
    PyTuple_SetItem(pArgs, 3, PyUnicode_FromString(args->local_uri));

    pValue = PyObject_CallObject(pFunc, pArgs);
    Py_XDECREF(pArgs);

    if (pValue == NULL) { PyErr_Print(); }
    Py_XDECREF(pValue);

cleanup:
    Py_XDECREF(pFunc);
    Py_XDECREF(pModule);
    if (libpython_handle) {
        Py_Finalize();
        dlclose(libpython_handle);
    }
    free(args->remote_uri);
    free(args->jobspec_str);
    free(args->local_uri);
    free(args);
    return NULL;
}

// depend_cb is expected for JobTap plugin
static int depend_cb(flux_plugin_t *p, const char *topic, flux_plugin_arg_t *args, void *arg) {
    thread_args_t *t_args = NULL;
    pthread_t thread_id;
    json_int_t id;
    const char *remote_uri_const, *local_uri_const;
    json_t *jobspec;

    if (flux_plugin_arg_unpack(args, FLUX_PLUGIN_ARG_IN, "{s:I s:{s:s} s:o}",
                               "id", &id, "dependency", "value", &remote_uri_const,
                               "jobspec", &jobspec) < 0) { return -1; }
    if (json_unpack(jobspec, "{s:{s:{s:{s:s}}}}", "attributes", "system", "delegate", "local_uri",
                    &local_uri_const) < 0) {
        return flux_jobtap_reject_job(p, args, "Missing attribute 'system.delegate.local_uri'");
    }
    if (flux_jobtap_dependency_add(p, id, "delegated") < 0) { return -1; }

    t_args = malloc(sizeof(thread_args_t));
    if (!t_args) { return -1; }
    t_args->jobid = id;
    t_args->remote_uri = strdup(remote_uri_const);
    t_args->local_uri = strdup(local_uri_const);
    t_args->jobspec_str = json_dumps(jobspec, 0);

    if (!t_args->remote_uri || !t_args->local_uri || !t_args->jobspec_str) {
        free(t_args->remote_uri); free(t_args->local_uri);
        free(t_args->jobspec_str); free(t_args);
        return -1;
    }
    if (pthread_create(&thread_id, NULL, worker_thread, t_args)) {
        free(t_args->remote_uri); free(t_args->local_uri);
        free(t_args->jobspec_str); free(t_args);
        return -1;
    }
    pthread_detach(thread_id);
    return 0;
}

static const struct flux_plugin_handler tab[] = {
    {"job.dependency.delegate", depend_cb, NULL}, {0},
};
int flux_plugin_init(flux_plugin_t *p) {
    return flux_plugin_register(p, "delegate-c-bridge", tab);
}