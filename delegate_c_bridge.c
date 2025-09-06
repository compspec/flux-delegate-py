/****************************************************************************
 * delegate_c_bridge.c
 *
 * A Flux jobtap plugin written in C that acts as a bridge to a Python script.
 * This plugin handles the 'job.dependency.delegate' topic by calling a
 * Python function to perform the actual delegation logic.
 ****************************************************************************/

#include <Python.h>       // Python C-API
#include <flux/jobtap.h>  // Flux jobtap plugin functions
#include <jansson.h>      // JSON handling from Flux

/*
 * Callback function that handles 'job.dependency.delegate' requests.
 * This is the main entry point from the Flux job manager.
 */
static int depend_cb(flux_plugin_t *p,
                     const char *topic,
                     flux_plugin_arg_t *args,
                     void *arg)
{
    // Variables to hold unpacked job data
    json_int_t id;
    const char *uri;
    json_t *jobspec;

    // Variables for the Python C-API
    PyObject *pName, *pModule, *pFunc;
    PyObject *pArgs, *pValue;
    long result;

    // Step 1: Unpack arguments from the Flux job manager.
    if (flux_plugin_arg_unpack(args, FLUX_PLUGIN_ARG_IN,
                               "{s:I s:{s:s} s:o}",
                               "id", &id,
                               "dependency", "value", &uri,
                               "jobspec", &jobspec) < 0) {
        return flux_jobtap_reject_job(p, args, "arg_unpack failed");
    }

    // Step 2: Initialize the Python interpreter.
    Py_Initialize();

    // Add the current directory "." to Python's sys.path.
    // This allows the interpreter to find the 'delegate_handler.py' script.
    // We can harden this, security wise, by choosing a system owned python file
    PyRun_SimpleString("import sys; sys.path.append('.')");

    // Step 3: Load the Python module (our .py file).
    // This could theoretically come from another source too.
    pName = PyUnicode_DecodeFSDefault("delegate_handler"); // The filename without .py
    pModule = PyImport_Import(pName);
    Py_DECREF(pName);

    if (pModule == NULL) {
        PyErr_Print(); // Print the Python import error to stderr
        fprintf(stderr, "Fatal: Failed to load 'delegate_handler.py'\n");
        Py_Finalize();
        return flux_jobtap_reject_job(p, args, "Python module not found");
    }

    // Step 4: Get a reference to the function we want to call.
    pFunc = PyObject_GetAttrString(pModule, "handle_delegation");
    if (!pFunc || !PyCallable_Check(pFunc)) {
        if (PyErr_Occurred()) PyErr_Print();
        fprintf(stderr, "Fatal: Cannot find function 'handle_delegation' in Python script\n");
        Py_DECREF(pModule);
        Py_Finalize();
        return flux_jobtap_reject_job(p, args, "Python function not found");
    }

    // Step 5: Build the arguments to pass to the Python function.
    pArgs = PyTuple_New(2); // We are passing 2 arguments.

    // Argument 1: The job ID
    pValue = PyLong_FromLongLong(id);
    PyTuple_SetItem(pArgs, 0, pValue); // pArgs takes ownership of pValue

    // Argument 2: The delegation URI
    pValue = PyUnicode_FromString(uri);
    PyTuple_SetItem(pArgs, 1, pValue); // pArgs takes ownership of pValue

    // Step 6: Call the Python function.
    pValue = PyObject_CallObject(pFunc, pArgs);
    Py_DECREF(pArgs);

    // Step 7: Check the return value from the Python function.
    if (pValue != NULL) {
        result = PyLong_AsLong(pValue); // Convert Python int to C long
        Py_DECREF(pValue);
    } else {
        PyErr_Print(); // An exception occurred in the Python code
        result = -1; // Indicate failure
    }

    // Step 8: Clean up the Python interpreter.
    Py_DECREF(pFunc);
    Py_DECREF(pModule);
    Py_Finalize();

    // Step 9: Return the final status to the Flux job manager.
    if (result == 0) {
        // The Python handler succeeded.
        // Signal to job manager that the dependency was handled successfully. 
        // The job will proceed based on this success.
        return 0;
    }

    // The Python handler returned a non-zero (failure) code.
    return flux_jobtap_reject_job(p, args, "Python handler failed");
}

// The handler table maps topics to callback functions.
static const struct flux_plugin_handler tab[] = {
    {"job.dependency.delegate", depend_cb, NULL},
    {0}, // Sentinel to mark the end of the table
};

// The main entry point called by Flux when the plugin is loaded.
int flux_plugin_init(flux_plugin_t *p) {
    // Register our plugin name and handler table.
    return flux_plugin_register(p, "delegate-c-bridge", tab);
}
