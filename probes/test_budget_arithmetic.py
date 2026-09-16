def test_proposed_budget_arithmetic():
    read = 1 + 2
    write = read + 4 + 1 + 30 + read + 2 * read
    assert write == 47
    cases = [1, 5, 9, 4, 5, 6, 1, 2, 1]
    assert sum(cases) == 34
    assert sum(cases) * write + 4 * read + 12 * read == 1646
    assert 3 + 6 + 4 * write + 39 + 6 + 36 == 278
