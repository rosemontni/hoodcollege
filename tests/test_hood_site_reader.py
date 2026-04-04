import unittest

from hood_pipeline.domain.models import SourceDefinition
from hood_pipeline.infrastructure.sources.hood_news import HoodSiteListingReader


class _FakeFetcher:
    def __init__(self, payloads: dict[str, str]) -> None:
        self.payloads = payloads
        self.requested_urls: list[str] = []

    def fetch_text(self, url: str) -> str:
        self.requested_urls.append(url)
        return self.payloads[url]


class HoodSiteListingReaderTest(unittest.TestCase):
    def test_reader_follows_pagination_and_collects_unique_news_articles(self) -> None:
        fetcher = _FakeFetcher(
            {
                "https://www.hood.edu/news": """
                    <html>
                      <body>
                        <a href="/news/first-story">First Story</a>
                        <a href="/news?page=1">Next page</a>
                        <a href="https://example.com/not-hood">Ignore me</a>
                      </body>
                    </html>
                """,
                "https://www.hood.edu/news?page=1": """
                    <html>
                      <body>
                        <a href="/news/second-story">Second Story</a>
                        <a href="/news/first-story">First Story</a>
                      </body>
                    </html>
                """,
            }
        )
        reader = HoodSiteListingReader(fetcher)
        definition = SourceDefinition(
            source_id="hood_news",
            name="Hood College News",
            reader="hood_site_listing",
            url="https://www.hood.edu/news",
            metadata={
                "domain": "www.hood.edu",
                "article_path_prefixes": ["/news/"],
                "max_listing_pages": 4,
            },
        )

        items = reader.read(definition)

        self.assertEqual(
            [item.url for item in items],
            [
                "https://www.hood.edu/news/first-story",
                "https://www.hood.edu/news/second-story",
            ],
        )
        self.assertEqual(
            fetcher.requested_urls,
            [
                "https://www.hood.edu/news",
                "https://www.hood.edu/news?page=1",
            ],
        )

    def test_reader_supports_story_listings_with_custom_article_prefix(self) -> None:
        fetcher = _FakeFetcher(
            {
                "https://www.hood.edu/discover/stories": """
                    <html>
                      <body>
                        <a href="/discover/stories/student-spotlight">Student Spotlight</a>
                        <a href="/news/not-a-story">News link</a>
                      </body>
                    </html>
                """
            }
        )
        reader = HoodSiteListingReader(fetcher)
        definition = SourceDefinition(
            source_id="hood_stories",
            name="Hood College Stories",
            reader="hood_site_listing",
            url="https://www.hood.edu/discover/stories",
            metadata={
                "domain": "www.hood.edu",
                "article_path_prefixes": ["/discover/stories/"],
            },
        )

        items = reader.read(definition)

        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].url, "https://www.hood.edu/discover/stories/student-spotlight")
        self.assertEqual(items[0].title, "Student Spotlight")

    def test_reader_can_filter_by_article_path_substring(self) -> None:
        fetcher = _FakeFetcher(
            {
                "https://www.fredericknewspost.com/search/?k=hood+college&t=article&f=html": """
                    <html>
                      <body>
                        <a href="/news/education/">Education section</a>
                        <a href="/news/education/hood-story/article_123.html">Hood story</a>
                        <a href="/site/contact.html">Contact</a>
                      </body>
                    </html>
                """
            }
        )
        reader = HoodSiteListingReader(fetcher)
        definition = SourceDefinition(
            source_id="frederick_news_post_search",
            name="Frederick News-Post search for Hood College",
            reader="hood_site_listing",
            url="https://www.fredericknewspost.com/search/?k=hood+college&t=article&f=html",
            metadata={
                "domain": "www.fredericknewspost.com",
                "article_path_prefixes": ["/"],
                "article_path_substrings_any": ["/article_"],
            },
        )

        items = reader.read(definition)

        self.assertEqual(len(items), 1)
        self.assertEqual(
            items[0].url,
            "https://www.fredericknewspost.com/news/education/hood-story/article_123.html",
        )
        self.assertEqual(items[0].title, "Hood story")


if __name__ == "__main__":
    unittest.main()
