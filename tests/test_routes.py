import pytest

PAGES = {
    "/": "Where it stands",
    "/accounts": "No transactions yet",
    "/investments": "No holdings yet",
    "/contact": "Open an issue",
}


@pytest.mark.parametrize("path,text", PAGES.items())
def test_pages_render_inside_the_layout(client, path, text):
    response = client.get(path)
    assert response.status_code == 200
    body = response.get_data(as_text=True)
    assert text in body
    assert '<nav aria-label="Main">' in body
    assert (
        "not financial advice" in body.lower() or "Nothing on this site is financial advice" in body
    )


@pytest.mark.parametrize("path", PAGES)
def test_current_page_is_marked_in_nav(client, path):
    body = client.get(path).get_data(as_text=True)
    assert body.count('aria-current="page"') == 1


def test_page_titles(client):
    assert "<title>Capital Catalyst</title>" in client.get("/").get_data(as_text=True)
    assert "<title>Accounts | Capital Catalyst</title>" in client.get("/accounts").get_data(
        as_text=True
    )


def test_unknown_page_returns_404_page(client):
    response = client.get("/does-not-exist")
    assert response.status_code == 404
    assert "Page not found" in response.get_data(as_text=True)


def test_wrong_method_returns_405_page(client):
    response = client.post("/")
    assert response.status_code == 405
    assert "Method not allowed" in response.get_data(as_text=True)


def test_server_error_returns_500_page(app):
    app.config["PROPAGATE_EXCEPTIONS"] = False

    @app.route("/boom")
    def boom():
        raise RuntimeError("boom")

    response = app.test_client().get("/boom")
    assert response.status_code == 500
    body = response.get_data(as_text=True)
    assert "Server error" in body
    assert "boom" not in body.split("<main", 1)[1]


@pytest.mark.parametrize("path", ["/", "/does-not-exist"])
def test_security_headers(client, path):
    headers = client.get(path).headers
    assert "frame-ancestors 'none'" in headers["Content-Security-Policy"]
    assert headers["X-Content-Type-Options"] == "nosniff"
    assert headers["X-Frame-Options"] == "DENY"
    assert headers["Referrer-Policy"] == "strict-origin-when-cross-origin"


def test_static_assets_are_served(client):
    for path in ["/static/css/main.css", "/static/favicon.svg"]:
        response = client.get(path)
        assert response.status_code == 200
        response.close()
