import os
import shutil
from dataclasses import dataclass
from typing import Generator

import pytest

import makesite
from test import path


@dataclass
class Site:
    blog_path: str
    site_path: str


@pytest.fixture
def site() -> Generator[Site, None, None]:
    blog_path = path.temppath("blog")
    site_path = path.temppath("site")
    os.makedirs(blog_path)

    with open(os.path.join(blog_path, "foo.txt"), "w") as f:
        f.write("Foo")
    with open(os.path.join(blog_path, "bar.txt"), "w") as f:
        f.write("Bar")
    with open(os.path.join(blog_path, "2018-01-01-foo.txt"), "w") as f:
        f.write("Foo")
    with open(os.path.join(blog_path, "2018-01-02-bar.txt"), "w") as f:
        f.write("Bar")
    with open(os.path.join(blog_path, "header-foo.txt"), "w") as f:
        f.write("<!-- tag: foo -->Foo")
    with open(os.path.join(blog_path, "header-bar.txt"), "w") as f:
        f.write("<!-- title: bar -->Bar")
    with open(os.path.join(blog_path, "placeholder-foo.txt"), "w") as f:
        f.write("<!-- title: foo -->{{ title }}:{{ author }}:Foo")
    with open(os.path.join(blog_path, "placeholder-bar.txt"), "w") as f:
        f.write("<!-- title: bar --><!-- render: yes -->{{ title }}:{{ author }}:Bar")

    yield Site(blog_path, site_path)

    shutil.rmtree(blog_path)
    shutil.rmtree(site_path)


class TestPages:
    def test_pages_undated(self, site):
        src = os.path.join(site.blog_path, "[fb]*.txt")
        dst = os.path.join(site.site_path, "{{ slug }}.txt")
        tpl = "<div>{{ content }}</div>"
        makesite.make_pages(src, dst, tpl)

        with open(os.path.join(site.site_path, "foo.txt")) as f:
            assert f.read() == "<div>Foo</div>"

        with open(os.path.join(site.site_path, "bar.txt")) as f:
            assert f.read() == "<div>Bar</div>"

    def test_pages_dated(self, site):
        src = os.path.join(site.blog_path, "2*.txt")
        dst = os.path.join(site.site_path, "{{ slug }}.txt")
        tpl = "<div>{{ content }}</div>"
        makesite.make_pages(src, dst, tpl)

        with open(os.path.join(site.site_path, "foo.txt")) as f:
            assert f.read() == "<div>Foo</div>"

        with open(os.path.join(site.site_path, "bar.txt")) as f:
            assert f.read() == "<div>Bar</div>"

    def test_pages_layout_params(self, site):
        src = os.path.join(site.blog_path, "2*.txt")
        dst = os.path.join(site.site_path, "{{ slug }}.txt")
        tpl = "<div>{{ slug }}:{{ title }}:{{ date }}:{{ content }}</div>"
        makesite.make_pages(src, dst, tpl, title="Lorem")

        with open(os.path.join(site.site_path, "foo.txt")) as f:
            assert f.read() == "<div>foo:Lorem:2018-01-01:Foo</div>"

        with open(os.path.join(site.site_path, "bar.txt")) as f:
            assert f.read() == "<div>bar:Lorem:2018-01-02:Bar</div>"

    def test_pages_return_value(self, site):
        src = os.path.join(site.blog_path, "2*.txt")
        dst = os.path.join(site.site_path, "{{ slug }}.txt")
        tpl = "<div>{{ content }}</div>"
        posts = makesite.make_pages(src, dst, tpl)

        assert len(posts) == 2
        assert posts[0]["date"] == "2018-01-02"
        assert posts[1]["date"] == "2018-01-01"

    def test_content_header_params(self, site):
        # Test that header params from one post is not used in another
        # post.
        src = os.path.join(site.blog_path, "header*.txt")
        dst = os.path.join(site.site_path, "{{ slug }}.txt")
        tpl = "{{ title }}:{{ tag }}:{{ content }}"
        makesite.make_pages(src, dst, tpl)

        with open(os.path.join(site.site_path, "header-foo.txt")) as f:
            assert f.read() == "{{ title }}:foo:Foo"

        with open(os.path.join(site.site_path, "header-bar.txt")) as f:
            assert f.read() == "bar:{{ tag }}:Bar"

    def test_content_no_rendering(self, site):
        # Test that placeholders are not populated in content rendering
        # by default.
        src = os.path.join(site.blog_path, "placeholder-foo.txt")
        dst = os.path.join(site.site_path, "{{ slug }}.txt")
        tpl = "<div>{{ content }}</div>"
        makesite.make_pages(src, dst, tpl, author="Admin")

        with open(os.path.join(site.site_path, "placeholder-foo.txt")) as f:
            assert f.read() == "<div>{{ title }}:{{ author }}:Foo</div>"

    def test_content_rendering_via_kwargs(self, site):
        # Test that placeholders are populated in content rendering when
        # requested in make_pages.
        src = os.path.join(site.blog_path, "placeholder-foo.txt")
        dst = os.path.join(site.site_path, "{{ slug }}.txt")
        tpl = "<div>{{ content }}</div>"
        makesite.make_pages(src, dst, tpl, author="Admin", render="yes")

        with open(os.path.join(site.site_path, "placeholder-foo.txt")) as f:
            assert f.read() == "<div>foo:Admin:Foo</div>"

    def test_content_rendering_via_header(self, site):
        # Test that placeholders are populated in content rendering when
        # requested in content header.
        src = os.path.join(site.blog_path, "placeholder-bar.txt")
        dst = os.path.join(site.site_path, "{{ slug }}.txt")
        tpl = "<div>{{ content }}</div>"
        makesite.make_pages(src, dst, tpl, author="Admin")

        with open(os.path.join(site.site_path, "placeholder-bar.txt")) as f:
            assert f.read() == "<div>bar:Admin:Bar</div>"

    @pytest.mark.xfail
    def test_rendered_content_in_summary(self, site):
        # Test that placeholders are populated in summary if and only if
        # content rendering is enabled.
        src = os.path.join(site.blog_path, "placeholder*.txt")
        post_dst = os.path.join(site.site_path, "{{ slug }}.txt")
        list_dst = os.path.join(site.site_path, "list.txt")
        post_layout = ""
        list_layout = "<div>{{ content }}</div>"
        item_layout = "<p>{{ summary }}</p>"
        posts = makesite.make_pages(src, post_dst, post_layout, author="Admin")
        makesite.make_list(posts, list_dst, list_layout, item_layout)

        with open(os.path.join(site.site_path, "list.txt")) as f:
            assert (
                f.read()
                == "<div><p>{{ title }}:{{ author }}:Foo</p><p>bar:Admin:Bar</p></div>"
            )
