# Test Suite
This test suite uses `pytest` and the public ownCloud server to run tests. See below on how to configure the tests to use other servers.

## How to run tests
This test suite assumes a fresh (unmodified) instance of the demo ownCloud server. The instance is automatically reset every hour.
```
python -m pytest -v
```
## Extending tests
To add new files to use during the testing process, simply copy them into the `testing/dummy_files` directory.

To configure the tests to use other servers, add it to the `SERVERS` dictionary. The dictionary stores a server address as the key and a 2-tuple of strings `(user, password)` as the corresponding value.