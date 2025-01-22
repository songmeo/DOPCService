import shutil
from pathlib import Path

import nox

BYPRODUCTS = [".coverage*", "*.log"]


@nox.session(python=False)
def clean(session: nox.Session) -> None:
    for w in BYPRODUCTS:
        for f in Path.cwd().glob(w):
            try:
                session.log(f"Removing: {f}")
                if f.is_dir():
                    shutil.rmtree(f, ignore_errors=True)
                else:
                    f.unlink(missing_ok=True)
            except Exception as ex:
                session.error(f"Failed to remove {f}: {ex}")


@nox.session(reuse_venv=True)
def mypy(session: nox.Session) -> None:
    session.install("-e", ".")
    session.install("mypy ~= 1.14")
    session.run("mypy", "src/")


@nox.session(reuse_venv=True)
def black(session: nox.Session) -> None:
    session.install("black ~= 24.10")
    session.run("black", "--check", ".")


@nox.session(reuse_venv=True)
def test(session: nox.Session) -> None:
    session.install("-e", ".")
    session.install("coverage ~= 7.6")

    # Run pytest with coverage
    session.install("pytest ~= 8.3")
    session.run("coverage", "run", "-m", "pytest")

    # Generate coverage report
    session.run("coverage", "combine")
    session.run("coverage", "report", "--fail-under=25")
