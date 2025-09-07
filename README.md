# Flux Delegate Python

This is a delgation plugin in Python, inspired by [Tapasya's](https://github.com/flux-framework/flux-core/pull/6873/files) WIP. I'm using it as a prototype until that one is ready, and I wanted to implement in Python as a proof of concept (since many like writing Python) and to make it easy to quickly update without recompiling something.

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