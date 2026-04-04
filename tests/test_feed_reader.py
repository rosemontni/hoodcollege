import unittest

from hood_pipeline.domain.models import SourceDefinition
from hood_pipeline.infrastructure.sources.hood_athletics import FeedReader


class _FakeFetcher:
    def __init__(self, payload: str) -> None:
        self.payload = payload

    def fetch_text(self, url: str) -> str:
        return self.payload

    def parse_rss_datetime(self, value: str | None):
        return value


class FeedReaderTest(unittest.TestCase):
    def test_reads_atom_feed_and_filters_reddit_comment_links(self) -> None:
        payload = """
            <feed xmlns="http://www.w3.org/2005/Atom">
              <entry>
                <title>FrederickMaryland</title>
                <link href="https://www.reddit.com/r/FrederickMaryland/" />
                <updated>2026-04-04T03:56:39+00:00</updated>
                <content type="html">&lt;div&gt;subreddit&lt;/div&gt;</content>
              </entry>
              <entry>
                <title>Hood College town hall thread</title>
                <link href="https://www.reddit.com/r/FrederickMaryland/comments/1abc123/hood_college_town_hall/" />
                <updated>2026-04-04T03:56:39+00:00</updated>
                <content type="html">&lt;div&gt;Discussing Hood College in Frederick.&lt;/div&gt;</content>
              </entry>
            </feed>
        """
        reader = FeedReader(_FakeFetcher(payload))
        definition = SourceDefinition(
            source_id="reddit_search",
            name="Reddit search",
            reader="feed",
            url="https://www.reddit.com/search.rss?q=hood",
            metadata={"item_url_contains_any": ["/comments/"]},
        )

        items = reader.read(definition)

        self.assertEqual(len(items), 1)
        self.assertEqual(
            items[0].url,
            "https://www.reddit.com/r/FrederickMaryland/comments/1abc123/hood_college_town_hall/",
        )
        self.assertEqual(items[0].title, "Hood College town hall thread")


if __name__ == "__main__":
    unittest.main()
