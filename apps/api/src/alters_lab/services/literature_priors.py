"""Literature priors service — load and query the curated prior catalog."""

from __future__ import annotations

from pathlib import Path

from alters_lab.schemas.literature_priors import (
    LiteraturePriorCatalog,
    load_literature_prior_catalog,
)


def get_catalog(repo_root: Path | None = None) -> LiteraturePriorCatalog:
    if repo_root:
        path = (
            repo_root
            / "alters"
            / "product"
            / "literature_priors"
            / "catalog"
            / "literature_prior_catalog_v0_1.yaml"
        )
        return load_literature_prior_catalog(path)
    return load_literature_prior_catalog()
