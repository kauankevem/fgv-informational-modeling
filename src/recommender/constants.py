"""Central location for feature definitions shared across modules."""

FEATURE_COLUMNS = ["anodelancamento", "duracaomin", "generonome", "estado"]
NUMERIC_COLUMNS = ["anodelancamento", "duracaomin"]
CATEGORICAL_COLUMNS = ["generonome", "estado"]
TOP_K_PER_STATE = 25
CANDIDATE_LIMIT = 400

