# Flux Delegate Python

This is a delgation plugin in Python, inspired by [Tapasya's](https://github.com/flux-framework/flux-core/pull/6873/files) WIP. I'm using it as a prototype until that one is ready, and I wanted to implement in Python as a proof of concept (since many like writing Python) and to make it easy to quickly update without recompiling something.

## Notes

We need to add a feasibility check, e.g., "Given these requests for software or other cluster resources, is this going to work?" Normally I think feasibility is run with fluxion, so *after* JobTap, but that doesn't make sense here. It doesn't make sense to send a job to another cluster just to have it rejected. So although this isn't a final design, I think feasibility (across many different options) needs to happen first. Then when we actually submit with a flux proxy (done via interfacing with the other URI) there is actually a better change of acceptance. It's like a pre-flight, fail fast check instead of "try and find out." An issue we might face is that the metadata about clusters and compatibility lives in a user's home, and I'm not sure that the flux instance / flux-core would have that access.

On the other hand, we don't want to add stress to flux-core to do these expensive checks for every job submit. So maybe what needs to happen is our library performs a local feasibility check, and _then_ formulates the submit request to the local Flux instance, and then the JobTap submits it. To the user, it is one command. And actually for our tool (fractale) we can wrap it in a flux command so it looks like a single flux command. Something like:

```bash
flux remote submit <same as flux submit>
```

The above is implemented to wrap around submit, and that is the extra command in [cmd](cmd) that can be installed to a Flux root (or just run as a one-off script). We just need to add the fractale stuff there. Will work on this week.

## Development

Open up the [.devcontainer](.devcontainer) is VSCode. then do:

```bash
./autogen.sh
./configure --prefix=/usr
make
sudo make install
```

## Usage

Once you have installed, you can test by starting a Flux broker in the same directory as [delegate_handler.py](delegate_handler.py).

```bash
make clean && ./autogen.sh && ./configure --prefix=/usr && make && sudo make install
flux broker --config-path=$(pwd)/delegate.toml
```

At this point you have your development environment, You can tweak the Python script and submit a job to test. If you crash the broker you'll need to restart again (happens sometimes with errors). I am now testing with the same URI.

```bash
flux submit --verbose --setattr=delegate.local_uri=$FLUX_URI --dependency=delegate:$FLUX_URI hostname
```
I added the local uri as an attribute because it would mean we can direct the interaction, saying exactly FROM where and TO where. I'm next wanting to think about how this fits into Fractale. We should have a lookup of clusters we know in the user's home, and then the URIs can come from there after a match is done. I also want to account for something with node features using NFD.

## Fractale

For integration with Fractale (and flux) we won't require the user to ask for delegation directly. We will provide a command for a remote submit:

```bash
flux remote submit --dry-run --setattr=requires.software=spack:curl curl
```

In the above, the user is asking for a remote submit. This means we are going to receive the request in Flux, compare to local subsystems and clusters defined by the user in their home, and then make a selection of a cluster. The selected cluster will go straight to the JobTap plugin from the `flux remote submit` command without the user needing any subsequent interaction.
What I want to work on / harden is the organization, structure, and query of the cluster and subsystem metadata. I've been forcing use of a graph but I am not convinced that is the best way.
See [examples/fractale](examples/fractale) for the full example, and the [cmd](cmd) that is added to Flux as a WIP to orchestrate this.
