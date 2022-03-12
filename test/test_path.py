import os
import shutil

from test import path


class TestPath:
    def test_temppath(self):
        assert path.temppath()

    def test_move_existing_file(self):
        src = os.path.join(path.temppath(), "foo.txt")
        dst = os.path.join(path.temppath(), "bar.txt")

        with open(src, "w") as f:
            f.write("foo")

        path.move(src, dst)

        assert not os.path.isfile(src)
        assert os.path.isfile(dst)

        with open(dst) as f:
            text = f.read()

        os.remove(dst)

        assert text == "foo"

    def test_move_missing_file(self):
        src = os.path.join(path.temppath(), "foo.txt")
        dst = os.path.join(path.temppath(), "bar.txt")
        path.move(src, dst)

        assert not os.path.isfile(src)
        assert not os.path.isfile(dst)

    def test_move_file_cleanup(self):
        src = os.path.join(path.temppath(), "foo.txt")
        dst = os.path.join(path.temppath(), "bar.txt")

        with open(dst, "w") as f:
            f.write("foo")

        path.move(src, dst)

        assert not os.path.isfile(src)
        assert not os.path.isfile(dst)

    def test_move_existing_dir(self):
        src = os.path.join(path.temppath(), "foo")
        srcf = os.path.join(src, "foo.txt")
        dst = os.path.join(path.temppath(), "bar")
        dstf = os.path.join(dst, "foo.txt")

        os.makedirs(src)

        with open(srcf, "w") as f:
            f.write("foo")

        path.move(src, dst)

        assert not os.path.isdir(src)
        assert os.path.isdir(dst)

        with open(dstf) as f:
            text = f.read()

        shutil.rmtree(dst)

        assert text == "foo"

    def test_move_missing_dir(self):
        src = os.path.join(path.temppath(), "foo")
        dst = os.path.join(path.temppath(), "bar")
        path.move(src, dst)

        assert not os.path.isdir(src)
        assert not os.path.isdir(dst)

    def test_move_dir_cleanup(self):
        src = os.path.join(path.temppath(), "foo")
        dst = os.path.join(path.temppath(), "bar")
        os.makedirs(dst)
        path.move(src, dst)

        assert not os.path.isdir(src)
        assert not os.path.isdir(dst)
