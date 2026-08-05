def test_new_phrase(client):
    response = client.get("/phrases/new")

    assert response.status_code == 200

    body = response.json()

    assert body == {
        "phrase": "war",
        "color": "#ff0000",
    }


def test_list_phrases(client, phrase_batch):
    response = client.get("/phrases")

    assert response.status_code == 200

    body = response.json()

    assert len(body) == len(phrase_batch)


def test_create_phrase(client):
    response = client.post(
        "/phrases",
        json={
            "phrase": "Ukraine",
            "color": "#123456",
        },
    )

    assert response.status_code == 201

    body = response.json()

    assert body["id"] is not None
    assert body["phrase"] == "Ukraine"
    assert body["color"] == "#123456"


def test_get_phrase(client, war_phrase):
    response = client.get(f"/phrases/{war_phrase.id}")

    assert response.status_code == 200

    body = response.json()

    assert body["id"] == war_phrase.id
    assert body["phrase"] == "war"


def test_get_missing_phrase(client):
    response = client.get("/phrases/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Phrase not found"


def test_update_phrase(client, war_phrase):
    response = client.put(
        f"/phrases/{war_phrase.id}",
        json={
            "phrase": "peace",
            "color": "#ffffff",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["phrase"] == "peace"
    assert body["color"] == "#ffffff"


def test_patch_phrase(client, war_phrase):
    response = client.patch(
        f"/phrases/{war_phrase.id}",
        json={
            "color": "#00ff00",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["phrase"] == "war"
    assert body["color"] == "#00ff00"


def test_delete_phrase(client, war_phrase):
    response = client.delete(f"/phrases/{war_phrase.id}")

    assert response.status_code == 200
    assert response.json() == {"ok": True}

    response = client.get(f"/phrases/{war_phrase.id}")

    assert response.status_code == 404


def test_update_missing_phrase(client):
    response = client.put(
        "/phrases/999999",
        json={
            "phrase": "foo",
            "color": "#000000",
        },
    )

    assert response.status_code == 404


def test_patch_missing_phrase(client):
    response = client.patch(
        "/phrases/999999",
        json={
            "phrase": "foo",
        },
    )

    assert response.status_code == 404


def test_delete_missing_phrase(client):
    response = client.delete("/phrases/999999")

    assert response.status_code == 404
