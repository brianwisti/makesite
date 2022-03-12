import shutil
import os
from dataclasses import dataclass
from typing import Generator

import pytest

import makesite
from test import path


@dataclass
class Pages:
    blog_path: str
    undated_path: str
    dated_path: str
    normal_post_path: str
    md_post_path: str
    no_md_post_path: str


@pytest.fixture
def pages() -> Generator[Pages, None, None]:
    blog_path = path.temppath("blog")
    undated_path = os.path.join(blog_path, "foo.txt")
    dated_path = os.path.join(blog_path, "2018-01-01-foo.txt")
    normal_post_path = os.path.join(blog_path, "baz.txt")
    md_post_path = os.path.join(blog_path, "qux.md")
    no_md_post_path = os.path.join(blog_path, "qux.txt")

    os.makedirs(blog_path)

    with open(undated_path, "w") as f:
        f.write("hello world")

    with open(dated_path, "w") as f:
        f.write("hello world")

    with open(normal_post_path, "w") as f:
        f.write("<!-- a: 1 -->\n<!-- b: 2 -->\nFoo")

    with open(md_post_path, "w") as f:
        f.write("*Foo*")

    with open(no_md_post_path, "w") as f:
        f.write("*Foo*")

    yield Pages(
        blog_path,
        undated_path,
        dated_path,
        normal_post_path,
        md_post_path,
        no_md_post_path,
    )

    shutil.rmtree(blog_path)


class TestContent:
    def test_content_content(self, pages):
        content = makesite.read_content(pages.undated_path)

        assert content["content"] == "hello world"

    def test_content_date(self, pages):
        content = makesite.read_content(pages.dated_path)

        assert content["date"] == "2018-01-01"

    def test_content_date_missing(self, pages):
        content = makesite.read_content(pages.undated_path)

        assert content["date"] == "1970-01-01"

    def test_content_slug_dated(self, pages):
        content = makesite.read_content(pages.dated_path)

        assert content["slug"] == "foo"

    def test_content_slug_undated(self, pages):
        content = makesite.read_content(pages.undated_path)

        assert content["slug"] == "foo"

    def test_content_headers(self, pages):
        content = makesite.read_content(pages.normal_post_path)

        assert content["a"] == "1"
        assert content["b"] == "2"
        assert content["content"] == "Foo"

    def test_markdown_rendering(self, pages):
        content = makesite.read_content(pages.md_post_path)
        assert content["content"] == "<p><em>Foo</em></p>\n"

    @pytest.mark.skip(reason="escape unittest so we can use fixtures")
    def test_markdown_import_error(self, pages, caplog):
        content = makesite.read_content(pages.md_post_path)
        assert content["content"] == "*Foo*"

        err = f"WARNING: Cannot render Markdown in {pages.md_post_path}: Error forced by text"
        assert err in caplog.text

    def test_no_markdown_rendering(self, pages):
        content = makesite.read_content(pages.no_md_post_path)

        assert content["content"] == "*Foo*"

    @pytest.mark.skip(reason="escape unittest so we can use fixtures")
    def test_no_markdown_import_error(self, pages, caplog):
        content = makesite.read_content(pages.no_md_post_path)

        assert content["content"] == "*Foo*"
        assert caplog.text is None
