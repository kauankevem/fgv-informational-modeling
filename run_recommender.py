"""CLI entrypoint to train and export the IMDb recommendation model."""

from __future__ import annotations

import logging
import sys

from src.recommender.pipeline import run_pipeline


def main() -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    )
    logger = logging.getLogger("run_recommender")
    try:
        run_pipeline()
    except Exception as exc:  # pragma: no cover - defensive logging path
        logger.exception("Falha ao executar o pipeline de recomendação: %s", exc)
        return 1
    logger.info("Pipeline executado com sucesso.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

