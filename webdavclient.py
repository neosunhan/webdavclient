import os.path
import requests
import xml.etree.ElementTree as ET
from urllib.parse import unquote, urlsplit

class WebDAVClient:
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
        if (response.status_code == 404):
            return []
        root = ET.fromstring(response.content)

        responses = []
        for response in root.findall("response", namespaces=WebDAVClient.namespace):
            res = {}
            res["Path"] = unquote(urlsplit(response.findtext("href", namespaces=WebDAVClient.namespace)).path)
            properties = response.find("propstat/prop", namespaces=WebDAVClient.namespace)
            if properties.find("resourcetype/collection", namespaces=WebDAVClient.namespace) is not None:
                res["Resource Type"] = "Folder"
                res["Name"] = res["Path"].split("/")[-2]
                res["Size"] = int(properties.findtext("quota-used-bytes", namespaces=WebDAVClient.namespace))
            else:
                res["Resource Type"] = "File"
                res["Name"] = res["Path"].split("/")[-1]
                res["Size"] = int(properties.findtext("getcontentlength", namespaces=WebDAVClient.namespace))
                res["Content Type"] = properties.findtext("getcontenttype", namespaces=WebDAVClient.namespace)
            res["Last Modified"] = properties.findtext("getlastmodified", namespaces=WebDAVClient.namespace)
            res["etag"] = properties.findtext("{DAV:}getetag", namespaces=WebDAVClient.namespace)
            responses.append(res)

        return responses

    def get(self, remote_path, local_path, auth=None):
        response = self.send_request("GET", remote_path, auth=auth)
        if os.path.isdir(local_path):
            local_path = os.path.join(local_path, os.path.basename(remote_path))
        with open(local_path, "wb") as local_file:
            for chunk in response.iter_content(chunk_size=self.chunk_size):
                local_file.write(chunk)
        return local_path

    def put(self, remote_path, local_path, auth=None):
        with open(local_path, "rb") as local_file:
            response = self.send_request("PUT", remote_path, data=local_file, auth=auth)
        return response.status_code

    def delete(self, remote_path, auth=None):
        response = self.send_request("DELETE", remote_path, auth=auth)
        return response.status_code

    def close(self):
        self.session.close()


if __name__ == "__main__":
    client = WebDAVClient("https://demo.owncloud.com/remote.php/dav/files/demo/", "demo", "demo")
    files = client.propfind("ownCloud Manual.pdf")
    files = client.propfind("test.txt")
    print(files)
    # for file in files:
    #     print(file)
    # client.get("Documents/Example.odt", "download/testdir/test.odt")
    # client.put("test.odt", "./download/test.odt")