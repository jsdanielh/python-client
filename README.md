# Nimiq Python Client

> Python implementation of the Albatross Nimiq RPC client specs.

## Usage

To get started sending requests to a Nimiq node, we create a `NimiqClient`
object.

```python
import asyncio
import nimiqclient

async with NimiqClient(
        scheme="http",
        user = "luna",
        password = "moon",
        host="127.0.0.1",
        port=8648
    ) as client:

    # Make RPC call to get consensus status
    consensus = await client.consensus()
    print("Consensus: {0}".format(consensus))
```

Note: When no `config` object is passed in the initialization it will use the
default values in the Nimiq node.

## API

The complete API documentation is available [here](https://jsdanielh.github.io/python-client/).

Check out the [Nimiq RPC specs](https://github.com/nimiq/core-rs-albatross/tree/albatross/rpc-server/src/dispatchers)
for the behind-the-scenes RPC calls.

## Installation

Clone the repository and install the package from source

```sh
git clone https://github.com/jsdanielh/python-client
cd python-client
python setup.py install
```

## Build

Clone the repo and install it

```sh
git clone https://github.com/jsdanielh/python-client
cd python-client
python setup.py install
```

All done, happy coding!

## Test

You need a start a Devnet Nimiq node:

```sh
# TODO: Add steps
```

Tests are stored in the `/tests` folder and can be run from the command line
like this:

```sh
python -m unittest discover -v
```

## Documentation

The documentation is generated automatically with [Sphinx](https://www.sphinx-doc.org).

From the repository root directory install the development dependency
requirements:

```sh
pip install -r requirements-dev.txt
```

Then from the `/docs` directory run Sphinx via the `make` command:

```sh
cd docs
make html
```

Add a blank file in the `/docs` folder with the name `.nojekyll` for the
documentation hosted on GitHub Pages:

```sh
touch .nojekyll
```

## Contributions

This implementation is based on the [original client](https://nimiq-community.github.io/python-client/)
developed by the Nimiq Community which was originally contributed by [rraallvv](https://github.com/rraallvv/).

Bug reports and pull requests are welcome! Please refer to the [issue tracker](https://github.com/jsdanielh/python-client/issues)
for ideas.

## License

[Apache 2.0](LICENSE.md)
