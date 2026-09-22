"""Test attribute selectors."""
import threading
from .. import util
import soupsieve as sv


class TestAttribute(util.TestCase):
    """Test attribute selectors."""

    MARKUP = """
    <div id="div">
    <p id="0">Some text <span id="1"> in a paragraph</span>.</p>
    <a id="2" href="http://google.com">Link</a>
    <span id="3">Direct child</span>
    <pre id="pre">
    <span id="4">Child 1</span>
    <span id="5">Child 2</span>
    <span id="6">Child 3</span>
    </pre>
    </div>
    """

    def test_attribute_not_equal_no_quotes(self):
        """Test attribute with value that does not equal specified value (no quotes)."""

        # No quotes
        self.assert_selector(
            self.MARKUP,
            'body [id!=\\35]',
            ["div", "0", "1", "2", "3", "pre", "4", "6"],
            flags=util.HTML5
        )

    def test_attribute_not_equal_quotes(self):
        """Test attribute with value that does not equal specified value (quotes)."""

        # Quotes
        self.assert_selector(
            self.MARKUP,
            "body [id!='5']",
            ["div", "0", "1", "2", "3", "pre", "4", "6"],
            flags=util.HTML5
        )

    def test_attribute_not_equal_double_quotes(self):
        """Test attribute with value that does not equal specified value (double quotes)."""

        # Double quotes
        self.assert_selector(
            self.MARKUP,
            'body [id!="5"]',
            ["div", "0", "1", "2", "3", "pre", "4", "6"],
            flags=util.HTML5
        )

    def test_bad_attribute_unclosed(self):
        """Test bad, unclosed attribute fails for syntax error, not timeout error."""

        results = []

        def compile_pattern():
            """Compile a pattern with an unclosed, quoted attribute value."""

            try:
                sv.compile('[a="' + ('x' * 300))
            except BaseException as e:  # noqa: B036
                results.append(e)

        # Run in a thread so a catastrophic backtrack shows up as a timeout
        # instead of hanging the test suite. `signal.alarm` is not portable.
        thread = threading.Thread(target=compile_pattern)
        thread.daemon = True
        thread.start()
        thread.join(10)
        self.assertFalse(thread.is_alive(), 'Pattern compile timed out (ReDoS)')
        self.assertTrue(results, 'Pattern compile did not fail')
        self.assertIsInstance(results[0], sv.SelectorSyntaxError)
