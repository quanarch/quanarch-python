# packages

The quas of this project live here. The quanar and every quan depend on them.

They are linked from this folder while you develop (`[tool.uv.sources]` in each
`pyproject.toml`). Once a qua is stable, publish it to a package index (PyPI, Nexus,
devpi, GitHub Packages…) and depend on the published version instead: quans built by
other teams, in other repositories, can then use the same contract.
