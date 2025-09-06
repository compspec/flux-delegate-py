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
flux broker --config-path=$(pwd)/delegate.toml
```

At this point you have your development environment, You can exit and restart the broker when you update the script.