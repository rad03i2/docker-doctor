# Contributing

Contributions are welcome when they keep Docker Doctor focused, deterministic, and safe.

1. Fork the repository and create a focused branch.
2. Use Python 3.10+ and install with `python -m pip install -e . pytest`.
3. Add or update tests for behavior changes.
4. Run `python -m compileall -q src tests` and `pytest -q`.
5. Keep diagnostics actionable and avoid rules that require executing untrusted project code.
6. Update the English and Arabic README sections when user-facing behavior changes.
7. Open a pull request describing the problem, approach, and validation performed.

Please do not commit credentials, generated environments, private Docker configuration, or third-party fixtures without permission.
