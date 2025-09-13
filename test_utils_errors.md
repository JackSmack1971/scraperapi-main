# test_utils

```
===================================================== test session starts ======================================================
platform linux -- Python 3.12.10, pytest-8.4.1, pluggy-1.6.0
rootdir: /workspace/scraperapi-main
collected 0 items / 1 error

============================================================ ERRORS ============================================================
_____________________________________________ ERROR collecting tests/test_utils.py _____________________________________________
ImportError while importing test module '/workspace/scraperapi-main/tests/test_utils.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/root/.pyenv/versions/3.12.10/lib/python3.12/importlib/__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests/test_utils.py:8: in <module>
    from utils import sanitize_url, configure_logging  # noqa: E402
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   ModuleNotFoundError: No module named 'utils'
=================================================== short test summary info ====================================================
ERROR tests/test_utils.py
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
======================================================= 1 error in 0.18s =======================================================

```
