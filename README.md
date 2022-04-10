# webdavclient
Simple prototype of a WebDAV client.

Provides the following operations:
- PROPFIND: list/stat folders and files
- GET: retrieve a file from the WebDAV server
- PUT: upload a file to an arbitrary path on the server
- DELETE: remove a file from the server

## How to use
Install dependencies
```
pip install -r requirements.txt
```
All functionality is contained within the WebDAVClient class
```python
from webdavclient import WebDAVClient

client = WebDAVClient("https://demo.owncloud.com/remote.php/dav/files/demo/", user="demo", password="demo")
items = client.propfind()
client.get("ownCloud Manual.pdf", "my_owncloud_manual.pdf")
client.put("test.txt", "example_file.txt")
```
Testing uses the `pytest` module
```
python -m pytest -v
```