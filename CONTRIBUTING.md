# Contributing to folder2kb

Thanks for your interest! Issues and pull requests are welcome.

## Reporting bugs / requesting features

Please use the issue templates on GitHub. For bugs, include your folder2kb version,
OS, Python version, the exact command you ran and the full error output.

## Development setup

```bash
git clone https://github.com/Xkongai/folder2kb.git
cd folder2kb
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
pytest -q
```

## Documentation

The README is available in three languages: [English](README.md), [简体中文](README.zh-CN.md)
and [日本語](README.ja.md). If you change one, please update the others too (or say in the PR
that a translation still needs updating). Images used by the READMEs live in `docs/images/`;
demo screenshots there show real `folder2kb` output, so please regenerate them rather than
editing the text by hand.

## Pull requests

- Keep changes focused; one feature or fix per PR.
- Add or update tests in `tests/` for behaviour changes.
- Make sure `pytest -q` passes before opening the PR.
- Update `CHANGELOG.md` under `[Unreleased]`.

By contributing, you agree that your contributions will be licensed under the MIT License.
