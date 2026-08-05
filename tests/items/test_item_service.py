from trakt_backend.items import FeedItem, FeedItemQuery, FeedItemService


def test_list_items(
    feed_item_service: FeedItemService,
    article_batch: list[FeedItem],
):
    items = feed_item_service.all(FeedItemQuery(limit=100, offset=0))

    assert len(article_batch) == 200
    assert len(items) == 100


def test_list_items_second_page(
    feed_item_service: FeedItemService,
    article_batch: list[FeedItem],
):
    items = feed_item_service.all(FeedItemQuery(limit=100, offset=100))

    assert len(items) == 100


def test_list_items_with_pagination(
    feed_item_service: FeedItemService,
    article_batch: list[FeedItem],
):
    query = FeedItemQuery(
        limit=10,
        offset=0,
    )

    items = feed_item_service.all(query)

    assert len(items) == 10


def test_get_item(
    feed_item_service: FeedItemService,
    news_article: FeedItem,
):
    item = feed_item_service.get(news_article.id)

    assert item is not None
    assert item.id == news_article.id


def test_get_item_not_found(
    feed_item_service: FeedItemService,
):
    assert feed_item_service.get("999999") is None


def test_mark_item_read(
    feed_item_service: FeedItemService,
    news_article: FeedItem,
):
    assert news_article.read_at is None
    assert news_article.read_later is False

    updated = feed_item_service.mark_read(news_article)

    assert updated.read_at is not None
    assert updated.read_later is False


def test_mark_item_read_clears_read_later(
    feed_item_service: FeedItemService,
    news_article: FeedItem,
):
    news_article.read_later = True

    feed_item_service.mark_read(news_article)

    assert news_article.read_at is not None
    assert news_article.read_later is False


def test_mark_item_read_later(
    feed_item_service: FeedItemService,
    news_article: FeedItem,
):
    assert news_article.read_later is False

    updated = feed_item_service.read_later(news_article)

    assert updated.read_later is True


def test_save_item(
    feed_item_service: FeedItemService,
    news_article: FeedItem,
):
    assert news_article.saved_at is None

    updated = feed_item_service.save(news_article)

    assert updated.saved_at is not None


def test_list_unread_items(
    feed_item_service: FeedItemService,
    article_batch: list[FeedItem],
):
    items = feed_item_service.all(FeedItemQuery(unread=True))

    assert all(item.read_at is None for item in items)


def test_list_read_items(
    feed_item_service: FeedItemService,
    article_batch: list[FeedItem],
):
    article_batch[0].read_at = None
    article_batch[1].read_at = article_batch[1].published_at

    items = feed_item_service.all(FeedItemQuery(unread=False))

    assert all(item.read_at is not None for item in items)


def test_list_saved_items(
    feed_item_service: FeedItemService,
    article_batch: list[FeedItem],
):
    article_batch[0].saved_at = article_batch[0].published_at

    items = feed_item_service.all(FeedItemQuery(saved=True))

    assert all(item.saved_at is not None for item in items)


def test_list_read_later_items(
    feed_item_service: FeedItemService,
    article_batch: list[FeedItem],
):
    article_batch[0].read_later = True

    items = feed_item_service.all(FeedItemQuery(read_later=True))

    assert all(item.read_later is True for item in items)


def test_bulk_mark_read(
    feed_item_service: FeedItemService,
    article_batch: list[FeedItem],
):
    item_ids = [item.id for item in article_batch[:3]]

    updated = feed_item_service.bulk_mark_read(item_ids)

    assert len(updated) == 3

    for item in updated:
        assert item.read_at is not None
        assert item.read_later is False


def test_bulk_read_later(
    feed_item_service: FeedItemService,
    article_batch: list[FeedItem],
):
    item_ids = [item.id for item in article_batch[:3]]

    updated = feed_item_service.bulk_read_later(item_ids)

    assert len(updated) == 3

    for item in updated:
        assert item.read_later is True


def test_bulk_save(
    feed_item_service: FeedItemService,
    article_batch: list[FeedItem],
):
    item_ids = [item.id for item in article_batch[:3]]

    updated = feed_item_service.bulk_save(item_ids)

    assert len(updated) == 3

    for item in updated:
        assert item.saved_at is not None


def test_bulk_mark_read_empty_list(
    feed_item_service: FeedItemService,
):
    result = feed_item_service.bulk_mark_read([])

    assert result == []


def test_bulk_read_later_empty_list(
    feed_item_service: FeedItemService,
):
    result = feed_item_service.bulk_read_later([])

    assert result == []


def test_bulk_save_empty_list(
    feed_item_service: FeedItemService,
):
    result = feed_item_service.bulk_save([])

    assert result == []


def test_group_scoped_items(
    session,
    news_group,
    nrk_feed,
    news_article,
):
    service = FeedItemService(
        session,
        group_scope_id=news_group.id,
    )

    items = service.all(FeedItemQuery())

    assert news_article.id in [item.id for item in items]


def test_feed_scoped_items(
    session,
    nrk_feed,
    news_article,
):
    service = FeedItemService(
        session,
        feed_scope_id=nrk_feed.id,
    )

    items = service.all(FeedItemQuery())

    assert news_article.id in [item.id for item in items]


def test_contains_returns_true_for_feed_scope(
    session,
    nrk_feed,
    news_article,
):
    service = FeedItemService(
        session,
        feed_scope_id=nrk_feed.id,
    )

    assert service.contains(news_article)


def test_contains_returns_false_for_wrong_feed_scope(
    session,
    tekno_feed,
    news_article,
):
    service = FeedItemService(
        session,
        feed_scope_id=tekno_feed.id,
    )

    assert not service.contains(news_article)


def test_contains_returns_true_for_group_scope(
    session,
    news_group,
    news_article,
):
    service = FeedItemService(
        session,
        group_scope_id=news_group.id,
    )

    assert service.contains(news_article)


def test_contains_returns_false_for_group_scope(
    session,
    technology_group,
    news_article,
):
    service = FeedItemService(
        session,
        group_scope_id=technology_group.id,
    )

    assert not service.contains(news_article)
