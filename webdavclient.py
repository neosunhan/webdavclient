import os.path
import requests
import xml.etree.ElementTree as ET
from urllib.parse import unquote, urlsplit

class Client:
    chunk_size = 10000
    namespace = {"": "DAV:"}

    def __init__(self, hostname, user=None, password=None, timeout=30):
        self.hostname = hostname
        self.timeout = timeout

        self.session = requests.Session()
        if user is not None and password is not None:
            self.session.auth = (user, password)

    def send_request(self, method, path="", **kwargs):
        path = os.path.join(self.hostname, path)
        kwargs.setdefault("timeout", self.timeout)
        response = self.session.request(method, path, **kwargs)
        return response

    def propfind(self, path="", auth=None):
        response = self.send_request("PROPFIND", path=path, headers={"Depth": "1"}, auth=auth)
        root = ET.fromstring(response.content)

        responses = []
        for response in root.findall("response", namespaces=Client.namespace):
            res = {}
            res["Path"] = unquote(urlsplit(response.findtext("href", namespaces=Client.namespace)).path)
            properties = response.find("propstat/prop", namespaces=Client.namespace)
            if properties.find("resourcetype/collection", namespaces=Client.namespace) is not None:
                res["Resource Type"] = "Folder"
                res["Name"] = res["Path"].split("/")[-2]
                res["Size"] = int(properties.findtext("quota-used-bytes", namespaces=Client.namespace))
            else:
                res["Resource"] = "File"
                res["Name"] = res["Path"].split("/")[-1]
                res["Size"] = int(properties.findtext("getcontentlength", namespaces=Client.namespace))
                res["Content Type"] = properties.findtext("getcontenttype", namespaces=Client.namespace)
            res["Last Modified"] = properties.findtext("getlastmodified", namespaces=Client.namespace)
            res["etag"] = properties.findtext("{DAV:}getetag", namespaces=Client.namespace)
            responses.append(res)

        return responses

    def get(self, remote_path, local_path, auth=None):
        response = self.send_request("GET", remote_path, auth=auth)
        if os.path.isdir(local_path):
            local_path = os.path.join(local_path, os.path.basename(remote_path))
        with open(local_path, "wb") as local_file:
            for chunk in response.iter_content(chunk_size=self.chunk_size):
                local_file.write(chunk)


if __name__ == "__main__":
    client = Client("https://demo.owncloud.com/remote.php/dav/files/demo/", "demo", "demo")
    # files = client.propfind()
    # for file in files:
    #     print(file)
    client.get("Documents/Example.odt", "download/testdir/test.odt")