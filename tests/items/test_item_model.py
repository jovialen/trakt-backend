import datetime
from time import struct_time

from trakt_backend.items import FeedItem, RSS2Item


def test_rss2item_import_from_parsed_maps_fields():
    entry = {
        "id": "item-1",
        "title": "Title",
        "link": "https://example.com/item",
        "summary": "Summary",
        "published_parsed": datetime.datetime(2024, 1, 1, 12, 0),
        "updated_parsed": datetime.datetime(2024, 1, 2, 12, 0),
        "authors": [{"name": "Alice"}],
        "tags": [{"term": "News"}, {"term": "Tech"}],
        "content": [{"value": "Content"}],
    }

    item = RSS2Item(
        title="",
        link="",
        summary="",
        published_at=datetime.datetime.now(),
        updated_at=datetime.datetime.now(),
        authors="",
        categories="",
        content="",
    )

    result = item.import_from_parsed(entry)

    assert result is item
    assert item.id == "item-1"
    assert item.title == "Title"
    assert item.link == "https://example.com/item"
    assert item.summary == "Summary"
    assert item.published_at == datetime.datetime(2024, 1, 1, 12, 0)
    assert item.updated_at == datetime.datetime(2024, 1, 2, 12, 0)
    assert item.authors == "Alice"
    assert item.categories == "News, Tech"
    assert item.content == "Content"


def test_rss2item_import_uses_id_before_guid_before_link():
    item = RSS2Item(
        title="",
        link="",
        summary="",
        published_at=datetime.datetime.now(),
        updated_at=datetime.datetime.now(),
        authors="",
        categories="",
        content="",
    )

    item.import_from_parsed(
        {
            "id": "id-value",
            "guid": "guid-value",
            "link": "link-value",
        }
    )

    assert item.id == "id-value"

    item.import_from_parsed(
        {
            "guid": "guid-value",
            "link": "link-value",
        }
    )

    assert item.id == "guid-value"

    item.import_from_parsed(
        {
            "link": "link-value",
        }
    )

    assert item.id == "link-value"


def test_rss2item_import_handles_missing_values():
    item = RSS2Item(
        title="",
        link="",
        summary="",
        published_at=datetime.datetime.now(),
        updated_at=datetime.datetime.now(),
        authors="",
        categories="",
        content="",
    )

    item.import_from_parsed({})

    assert item.id == ""
    assert item.title == ""
    assert item.link == ""
    assert item.summary == ""
    assert item.authors == ""
    assert item.categories == ""
    assert item.content == ""


def test_rss2item_import_maps_multiple_authors():
    item = RSS2Item(
        title="",
        link="",
        summary="",
        published_at=datetime.datetime.now(),
        updated_at=datetime.datetime.now(),
        authors="",
        categories="",
        content="",
    )

    item.import_from_parsed(
        {
            "authors": [
                {"name": "Alice"},
                {"name": "Bob"},
                {},
            ]
        }
    )

    assert item.authors == "Alice, Bob"


def test_rss2item_import_falls_back_to_author():
    item = RSS2Item(
        title="",
        link="",
        summary="",
        published_at=datetime.datetime.now(),
        updated_at=datetime.datetime.now(),
        authors="",
        categories="",
        content="",
    )

    item.import_from_parsed({"author": "Alice"})

    assert item.authors == "Alice"


def test_rss2item_import_maps_multiple_content_blocks():
    item = RSS2Item(
        title="",
        link="",
        summary="",
        published_at=datetime.datetime.now(),
        updated_at=datetime.datetime.now(),
        authors="",
        categories="",
        content="",
    )

    item.import_from_parsed(
        {
            "content": [
                {"value": "First"},
                {"value": "Second"},
            ]
        }
    )

    assert item.content == "First\n\nSecond"


def test_parse_feed_time_returns_datetime_unchanged():
    value = datetime.datetime(2024, 1, 1)

    assert RSS2Item._parse_feed_time(value) == value


def test_parse_feed_time_converts_struct_time():
    value = struct_time((2024, 1, 2, 12, 30, 0, 0, 0, -1))

    result = RSS2Item._parse_feed_time(value)

    assert result == datetime.datetime(2024, 1, 2, 12, 30, 0)


def test_parse_feed_time_none_returns_datetime():
    result = RSS2Item._parse_feed_time(None)

    assert isinstance(result, datetime.datetime)


def test_feed_item_defaults():
    item = FeedItem(
        id="item-1",
        title="Title",
        link="https://example.com",
        summary="Summary",
        published_at=datetime.datetime.now(),
        updated_at=datetime.datetime.now(),
        authors="Author",
        categories="Category",
        content="Content",
        feed_id=1,
    )

    assert item.read_at is None
    assert item.read_later is False
    assert item.saved_at is None
