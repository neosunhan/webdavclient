import os
import pytest
from webdavclient import WebDAVClient

DUMMY_FILES = "tests/dummy_files"

@pytest.fixture
def client():
    client_instance = WebDAVClient("https://demo.owncloud.com/remote.php/dav/files/demo/", "demo", "demo")
    yield client_instance
    client_instance.close()

def test_propfind(client):
    items = client.propfind()
    assert any(item["Name"] == "Documents" and item["Resource Type"] == "Folder" for item in items)
    assert any(item["Name"] == "ownCloud Manual.pdf" and item["Resource Type"] == "File" for item in items)
    photos = client.propfind("Photos")
    assert any(photo["Name"] == "Lake-Constance.jpg" and photo["Resource Type"] == "File" for photo in photos)


@pytest.fixture(params=os.listdir(DUMMY_FILES))
def upload_file(client, request):
    remote_path = request.param
    if len(client.propfind(remote_path)) > 0:
        pytest.skip("{remote_path} already exists")
    client.put(remote_path, os.path.join(DUMMY_FILES, request.param))
    yield request.param
    client.delete(remote_path)

#TODO test overwrite files 

def test_put(client, upload_file):
    assert any(item["Name"] == upload_file for item in client.propfind())

@pytest.fixture
def download_file(client, upload_file, tmpdir):
    client.get(upload_file, tmpdir)
    yield upload_file
    
#TODO write to different name

def test_get(upload_file, download_file, tmpdir):
    assert len(tmpdir.listdir()) == 1
    with open(os.path.join(DUMMY_FILES, upload_file), "rb") as original:
        with open(tmpdir / download_file, "rb") as downloaded:
            assert original.read() == downloaded.read()