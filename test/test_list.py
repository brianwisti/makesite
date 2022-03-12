import shutil
import os
from typing import Generator

import pytest

import makesite
from test import path


@pytest.fixture
def site_path() -> Generator[str, None, None]:
    tmp_path = path.temppath("site")

    yield tmp_path

    shutil.rmtree(tmp_path)


class TestPages:
    def test_list(self, site_path):
        posts = [{"content": "Foo"}, {"content": "Bar"}]
        dst = os.path.join(site_path, "list.txt")
        list_layout = "<div>{{ content }}</div>"
        item_layout = "<p>{{ content }}</p>"
        makesite.make_list(posts, dst, list_layout, item_layout)

        with open(os.path.join(site_path, "list.txt")) as f:
            assert f.read() == "<div><p>Foo</p><p>Bar</p></div>"

    def test_list_params(self, site_path):
        posts = [{"content": "Foo", "title": "foo"}, {"content": "Bar", "title": "bar"}]
        dst = os.path.join(site_path, "list.txt")
        list_layout = "<div>{{ key }}:{{ title }}:{{ content }}</div>"
        item_layout = "<p>{{ key }}:{{ title }}:{{ content }}</p>"
        makesite.make_list(
            posts, dst, list_layout, item_layout, key="val", title="lorem"
        )

        with open(os.path.join(site_path, "list.txt")) as f:
            text = f.read()
            assert text == "<div>val:lorem:<p>val:foo:Foo</p><p>val:bar:Bar</p></div>"

    def test_dst_params(self, site_path):
        posts = [{"content": "Foo"}, {"content": "Bar"}]
        dst = os.path.join(site_path, "{{ key }}.txt")
        list_layout = "<div>{{ content }}</div>"
        item_layout = "<p>{{ content }}</p>"
        makesite.make_list(posts, dst, list_layout, item_layout, key="val")
        expected_path = os.path.join(site_path, "val.txt")

        assert os.path.isfile(expected_path)

        with open(expected_path) as f:
            assert f.read() == "<div><p>Foo</p><p>Bar</p></div>"
