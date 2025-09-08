# Fractale Workflow

This example will walk through the steps to generate local compatibility graphs to describe a user-space, and then use `flux remote` to submit with the JobTap delegation plugin. 

## Install Fractale

You can pip install, or install from GitHub.

```bash
pip install fractale

# or
git clone https://github.com/compspec/fractale
cd fractale
pip install -e .
```

## Local Subsystems

A local subsystem is typically a user-space install of software or other metadata that is associated with a cluster. Local subsystems can be defined for one or more clusters, and all provided to fractale to determine with of the clusters can support the work. For each cluster, the user will use fractale and (via the [compspec](https://github.com/compspec/compspec) library and plugins) generate one or more subsystem graphs associated with different clusters. Let's start with generating metadata for clusters A and B:

```bash
fractale generate --cluster A spack /home/vanessa/Desktop/Code/spack
```

I'm still thinking of how I want these generated and organized. I'm not convinced forcing a graph is the best way. Arguably, each plugin should be able to independently decide and then deliver
its organized information to a common interface.

## Remote Submit Request

Satisfy asks two questions:

1. Which clusters have the subsystem resources that I need?
2. Which clusters have the job resources that I need (containment subsystem)?

This is the step where we want to say "Run gromacs on 2-4 nodes with these requirements." Since we haven't formalized a way to do that, I'm going to start with a flux jobspec, and then add attributes that can be used to search our subsystems. For example (and currently there are two ways to do this):

```bash
flux remote submit --dry-run --setattr=requires.software=spack:curl curl
```
