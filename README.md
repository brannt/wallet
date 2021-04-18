# wallet

<div align="center">

[![Build status](https://github.com/brannt/wallet/workflows/build/badge.svg?branch=master&event=push)](https://github.com/brannt/wallet/actions?query=workflow%3Abuild)
[![Python Version](https://img.shields.io/pypi/pyversions/wallet.svg)](https://pypi.org/project/wallet/)
[![Dependencies Status](https://img.shields.io/badge/dependencies-up%20to%20date-brightgreen.svg)](https://github.com/brannt/wallet/pulls?utf8=%E2%9C%93&q=is%3Apr%20author%3Aapp%2Fdependabot)

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Security: bandit](https://img.shields.io/badge/security-bandit-green.svg)](https://github.com/PyCQA/bandit)
[![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/brannt/wallet/blob/master/.pre-commit-config.yaml)
[![Semantic Versions](https://img.shields.io/badge/%F0%9F%9A%80-semantic%20versions-informational.svg)](https://github.com/brannt/wallet/releases)
[![License](https://img.shields.io/github/license/brannt/wallet)](https://github.com/brannt/wallet/blob/master/LICENSE)

Wallet payments API created as a test task.

To bring the project up:

```bash
make compose_up
```

To run the tests on MySQL:

```bash
make compose_test
```

### Makefile usage

[`Makefile`](https://github.com/brannt/wallet/blob/master/Makefile) contains many functions for fast assembling and convenient work.

<details>
<summary>1. Download Poetry</summary>
<p>

```bash
make download-poetry
```

</p>
</details>

<details>
<summary>2. Install all dependencies and pre-commit hooks</summary>
<p>

```bash
make install
```

If you do not want to install pre-commit hooks, run the command with the NO_PRE_COMMIT flag:

```bash
make install NO_PRE_COMMIT=1
```

</p>
</details>

<details>
<summary>3. Check the security of your code</summary>
<p>

```bash
make check-safety
```

This command launches a `Poetry` and `Pip` integrity check as well as identifies security issues with `Safety` and `Bandit`. By default, the build will not crash if any of the items fail. But you can set `STRICT=1` for the entire build, or you can configure strictness for each item separately.

```bash
make check-safety STRICT=1
```

or only for `safety`:

```bash
make check-safety SAFETY_STRICT=1
```

multiple

```bash
make check-safety PIP_STRICT=1 SAFETY_STRICT=1
```

> List of flags for `check-safety` (can be set to `1` or `0`): `STRICT`, `POETRY_STRICT`, `PIP_STRICT`, `SAFETY_STRICT`, `BANDIT_STRICT`.

</p>
</details>

<details>
<summary>4. Check the codestyle</summary>
<p>

The command is similar to `check-safety` but to check the code style, obviously. It uses `Black`, `Darglint`, `Isort`, and `Mypy` inside.

```bash
make check-style
```

It may also contain the `STRICT` flag.

```bash
make check-style STRICT=1
```

> List of flags for `check-style` (can be set to `1` or `0`): `STRICT`, `BLACK_STRICT`, `DARGLINT_STRICT`, `ISORT_STRICT`, `MYPY_STRICT`.

</p>
</details>

<details>
<summary>5. Run all the codestyle formaters</summary>
<p>

Codestyle uses `pre-commit` hooks, so ensure you've run `make install` before.

```bash
make codestyle
```

</p>
</details>

<details>
<summary>6. Run tests</summary>
<p>

```bash
make test
```

</p>
</details>

<details>
<summary>7. Run all the linters</summary>
<p>

```bash
make lint
```

the same as:

```bash
make test && make check-safety && make check-style
```

> List of flags for `lint` (can be set to `1` or `0`): `STRICT`, `POETRY_STRICT`, `PIP_STRICT`, `SAFETY_STRICT`, `BANDIT_STRICT`, `BLACK_STRICT`, `DARGLINT_STRICT`, `ISORT_STRICT`, `MYPY_STRICT`.

</p>
</details>

<details>
<summary>8. Build docker</summary>
<p>

```bash
make docker
```

which is equivalent to:

```bash
make docker VERSION=latest
```

More information [here](https://github.com/brannt/wallet/tree/master/docker).

</p>
</details>

<details>
<summary>9. Cleanup docker</summary>
<p>

```bash
make clean_docker
```

or to remove all build

```bash
make clean
```
</p>

</details>
<details>
<summary>10. Docker-compose commands</summary>
<p>
Start the environment:
  
```bash
make compose_up
```

(Re)build the environment:

```bash
make compose_build
```

Start the environment in dev mode (dev and test dependencies installed, uvicorn with `--reload` instead of gunicorn-hosted):

```bash
make compose_up_dev
```

(Re)build the environment in test mode:

```bash
make compose_build_dev
```

Run tests on MySQL database (as opposed to SQLite); requires that the environment is in dev mode:

```bash
make compose_test
```

</p>
</details>

## 📈 Releases

You can see the list of available releases on the [GitHub Releases](https://github.com/brannt/wallet/releases) page.

We follow [Semantic Versions](https://semver.org/) specification.

```
@misc{wallet,
  author = {brannt},
  title = {Wallet payments API created as a test task},
  year = {2021},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{https://github.com/brannt/wallet}}
}
```

## Credits

This project was generated with [`python-package-template`](https://github.com/TezRomacH/python-package-template).
