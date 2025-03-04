import makesite


class TestTruncate:
    def test_truncate(self):
        long_text = "  \n".join("word" + str(i) for i in range(50))
        expected_text = " ".join("word" + str(i) for i in range(25))

        assert makesite.truncate(long_text) == expected_text
