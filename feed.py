import feedparser
from llama_index.core import Document
from llama_index.core.schema import MetadataMode
import uuid
import hashlib
default_rss_feeds = ["https://rss.nytimes.com/services/xml/rss/nyt/World.xml", 
                 "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml", 
                 "https://rss.nytimes.com/services/xml/rss/nyt/PersonalTech.xml",
                 "https://rss.nytimes.com/services/xml/rss/nyt/Science.xml",
                 "https://rss.nytimes.com/services/xml/rss/nyt/Health.xml",
                 ]

def create_uuid_from_string(val: str):
    hex_string = hashlib.md5(val.encode("UTF-8")).hexdigest()
    return uuid.UUID(hex=hex_string)
class Feed:
    def __init__(self, rss_feed_urls=None):
        self.rss_feed_urls = rss_feed_urls if rss_feed_urls else default_rss_feeds
        self.documents = []

    def get_documents(self):
        print("Fetching documents from RSS feeds...")
        print("RSS feed URLs:")
        for url in self.rss_feed_urls:
            print(f"- {url}")
        for url in self.rss_feed_urls:
            feed = feedparser.parse(url)
            for entry in feed.entries:
                # print(create_uuid_from_string(entry.link))
                self.documents.append(Document(
                    doc_id=create_uuid_from_string(entry.link).hex,
                    text=entry.title + " - " + entry.summary,
                    metadata={
                        "source": feed["feed"]["title"],
                        "link": entry.link,
                        "date": entry.published,
                        "image": entry.media_content[0]["url"] if "media_content" in entry else "No image",
                        "tags": str([tag.term for tag in entry.tags]) if "tags" in entry else "No tags",
                    },
                    excluded_embed_metadata_keys=["image", "link"],
                    metadata_seperator="::",
                    metadata_template="{key}=>{value}",
                    text_template="Details: {metadata_str}\nArticle: {content}",
                ))
        return self.documents

    def get_feed_info(self):
        return self.feed.feed
    
if __name__ == "__main__":
    rss_feed_urls = ["https://rss.nytimes.com/services/xml/rss/nyt/World.xml", 
                 "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml", 
                 "https://rss.nytimes.com/services/xml/rss/nyt/PersonalTech.xml",
                 "https://rss.nytimes.com/services/xml/rss/nyt/Science.xml",
                 "https://rss.nytimes.com/services/xml/rss/nyt/Health.xml",
                 ]
    feed = Feed(rss_feed_urls)
    documents = feed.get_documents()
    for document in documents:
        print(document.get_content(metadata_mode=MetadataMode.EMBED))
        # print(document.metadata)
        print("\n")