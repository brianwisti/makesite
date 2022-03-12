import os
import shutil
import json

import pytest

import makesite
from test import path


@pytest.fixture(autouse=True)
def prep():
    path.move("_site", "_site.backup")
    path.move("params.json", "params.json.backup")

    yield

    path.move("_site.backup", "_site")
    path.move("params.json.backup", "params")


class TestMain:
    def test_site_missing(self):
        makesite.main()

    def test_site_exists(self):
        os.mkdir("_site")
        with open("_site/foo.txt", "w") as f:
            f.write("foo")

        assert os.path.isfile("_site/foo.txt")
        makesite.main()

        assert not os.path.isfile("_site/foo.txt")

    def test_default_params(self):
        makesite.main()

        with open("_site/blog/proin-quam/index.html") as f:
            s1 = f.read()

        with open("_site/blog/rss.xml") as f:
            s2 = f.read()

        shutil.rmtree("_site")

        assert '<a href="/">Home</a>' in s1
        assert "<title>Proin Quam - Lorem Ipsum</title>" in s1
        assert "Published on 2018-01-01 by <b>Admin</b>" in s1
        assert "<link>http://localhost:8000/</link>" in s2
        assert "<link>http://localhost:8000/blog/proin-quam/</link>" in s2

    def test_json_params(self):
        params = {
            "base_path": "/base",
            "subtitle": "Foo",
            "author": "Bar",
            "site_url": "http://localhost/base",
        }

        with open("params.json", "w") as f:
            json.dump(params, f)

        makesite.main()

        with open("_site/blog/proin-quam/index.html") as f:
            s1 = f.read()

        with open("_site/blog/rss.xml") as f:
            s2 = f.read()

        shutil.rmtree("_site")

        assert '<a href="/base/">Home</a>' in s1
        assert "<title>Proin Quam - Foo</title>" in s1
        assert "Published on 2018-01-01 by <b>Bar</b>" in s1

        assert "<link>http://localhost/base/</link>" in s2
        assert "<link>http://localhost/base/blog/proin-quam/</link>" in s2
