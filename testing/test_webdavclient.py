import pytest

from exceptions import RemoteResourceNotFoundException, UnauthorizedException
from pathlib import Path
from webdavclient import WebDAVClient

DUMMY_FILES = Path("testing/dummy_files")
SERVERS = {"https://demo.owncloud.com/remote.php/dav/files/demo/": ("demo", "demo")}

class TestPropfind:
    def test_propfind(self, client):
        items = client.propfind()
        assert any(item["Name"] == "Documents" and item["Resource Type"] == "Folder" for item in items)
        assert any(item["Name"] == "ownCloud Manual.pdf" and item["Resource Type"] == "File" for item in items)
        documents = client.propfind("Documents")
        assert any(doc["Name"] == "Example.odt" and doc["Resource Type"] == "File" for doc in documents)

    def test_unauthorized(self, client_unauthorized, server_auth_pair):
        with pytest.raises(UnauthorizedException):
            client_unauthorized.propfind()
        items = client_unauthorized.propfind(auth=server_auth_pair[1])
        assert any(item["Name"] == "Documents" and item["Resource Type"] == "Folder" for item in items)

    def test_remote_path_not_found(self, client, nonexistent_path):
        with pytest.raises(RemoteResourceNotFoundException):
            client.propfind(nonexistent_path.as_posix())

class TestPut:
    def test_put(self, client, remote_path, local_path):
        client.put(remote_path.as_posix(), local_path)
        assert any(item["Name"] == remote_path.name for item in client.propfind(remote_path.as_posix()))

    def test_illegal_remote_path(self, client, local_path_single, nonexistent_path):
        fake_path = nonexistent_path / local_path_single.name
        with pytest.raises(RemoteResourceNotFoundException):
            client.put(fake_path.as_posix(), local_path_single)
        with pytest.raises(ValueError):
            client.put("", local_path_single)

    def test_illegal_local_path(self, client, local_path_single, nonexistent_path):
        with pytest.raises(FileNotFoundError):
            client.put(local_path_single.name, nonexistent_path)

class TestGet:
    def test_get(self, client, local_path, uploaded_file, tmpdir):
        tmpfile = tmpdir / uploaded_file.name
        client.get(uploaded_file.as_posix(), tmpfile)
        with open(local_path, "rb") as original:
            with open(tmpfile, "rb") as downloaded:
                assert original.read() == downloaded.read()

    def test_illegal_remote_path(self, client, local_path_single, nonexistent_path, tmpdir):
        fake_path = nonexistent_path / local_path_single.name
        with pytest.raises(RemoteResourceNotFoundException):
            client.get(fake_path.as_posix(), tmpdir)
        
    def test_illegal_local_path(self, client, uploaded_file_single, nonexistent_path):
        illegal_local_path = nonexistent_path / "illegal.txt"
        with pytest.raises(FileNotFoundError):
            client.get(uploaded_file_single.as_posix(), illegal_local_path)

@pytest.fixture(params=SERVERS.items())
def server_auth_pair(request):
    return request.param

@pytest.fixture
def client_unauthorized(server_auth_pair):
    client_instance = WebDAVClient(server_auth_pair[0])
    yield client_instance
    client_instance.close()

@pytest.fixture
def client(server_auth_pair):
    client_instance = WebDAVClient(server_auth_pair[0], *server_auth_pair[1])
    yield client_instance
    client_instance.close()

@pytest.fixture(params=DUMMY_FILES.iterdir())
def local_path(request):
    return request.param

@pytest.fixture
def local_path_single():
    try:
        first = next(DUMMY_FILES.iterdir())
    except StopIteration:
        pytest.skip(f"No files in {DUMMY_FILES}")
    return first

@pytest.fixture(params=["", "Documents"])
def remote_path(client, local_path, request):
    file_name = local_path.name
    remote_dir = Path(request.param)
    full_path = remote_dir / file_name
    if any(item["Name"] == file_name for item in client.propfind(remote_dir.as_posix())):
        pytest.skip(f"{full_path.as_posix()} already exists")
    yield full_path
    if any(item["Name"] == file_name for item in client.propfind(remote_dir.as_posix())):
        client.delete(full_path.as_posix())

@pytest.fixture
def uploaded_file(client, remote_path, local_path):
    client.put(remote_path.as_posix(), local_path)
    yield remote_path
    client.delete(remote_path.as_posix())

@pytest.fixture
def uploaded_file_single(client, local_path_single):
    remote_path = Path(local_path_single.name)
    if any(item["Name"] == local_path_single.name for item in client.propfind()):
        pytest.skip(f"{remote_path} already exists")
    client.put(remote_path.as_posix(), local_path_single)
    yield remote_path
    client.delete(remote_path.as_posix())

@pytest.fixture
def nonexistent_path():
    return Path("this_path_does_not_exist")