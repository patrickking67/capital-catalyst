def run(app, *args, input=None):
    return app.test_cli_runner().invoke(args=list(args), input=input)


def make_user(app, name="alex", secret="correct horse battery"):  # noqa: S107
    return run(app, "create-user", name, input=f"{secret}\n{secret}\n")


def test_create_user_hashes_password_and_rejects_duplicates(app):
    result = make_user(app)
    assert result.exit_code == 0
    assert "Created user alex." in result.output
    assert "correct horse" not in result.output
    again = make_user(app)
    assert again.exit_code == 1
    assert "already exists" in again.output


def test_create_user_validates(app):
    assert "username must be" in make_user(app, name="no good").output
    short = make_user(app, name="sam", secret="short")
    assert short.exit_code == 1
    assert "at least 8" in short.output


def test_transactions_and_balances_round_trip(app):
    make_user(app)
    assert run(app, "add-transaction", "alex", "Checking", "1200.50").exit_code == 0
    assert run(app, "add-transaction", "alex", "Checking", "-200").exit_code == 0
    result = run(app, "balances", "alex")
    assert result.output.strip() == "Checking: 1,000.50"


def test_bad_amount_is_reported_not_saved(app):
    make_user(app)
    result = run(app, "add-transaction", "alex", "Checking", "1.005")
    assert result.exit_code == 1
    assert "2 decimal places" in result.output
    assert run(app, "balances", "alex").output.strip() == "No transactions recorded."


def test_holdings_round_trip_without_values(app):
    make_user(app)
    run(app, "add-holding", "alex", "Index fund", "1.5")
    run(app, "add-holding", "alex", "Index fund", "0.25")
    result = run(app, "holdings", "alex")
    assert result.output.strip() == "Index fund: 1.75"
    assert "$" not in result.output


def test_unknown_user_is_a_clear_error(app):
    for command in (
        ["balances", "ghost"],
        ["holdings", "ghost"],
        ["add-holding", "ghost", "X", "1"],
    ):
        result = run(app, *command)
        assert result.exit_code == 1
        assert "No user named 'ghost'" in result.output


def test_empty_listings(app):
    make_user(app)
    assert run(app, "holdings", "alex").output.strip() == "No holdings recorded."
