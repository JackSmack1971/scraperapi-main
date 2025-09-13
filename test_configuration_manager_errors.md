# test_configuration_manager

```
===================================================== test session starts ======================================================
platform linux -- Python 3.12.10, pytest-8.4.1, pluggy-1.6.0
rootdir: /workspace/scraperapi-main
collected 3 items

tests/test_configuration_manager.py ...                                                                                  [100%]

======================================================= warnings summary =======================================================
tests/test_configuration_manager.py::test_save_template_sanitizes_name
  /workspace/scraperapi-main/ui.py:203: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    "created": datetime.utcnow().isoformat() + "Z",

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
================================================= 3 passed, 1 warning in 0.79s =================================================

```
