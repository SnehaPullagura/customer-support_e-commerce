"""
Product Category and Return Policy Taxonomy Registry.
"""

from app.domain.taxonomy.categories import (
    CategoryPolicy,
    CategoryTaxonomyService,
    ENTERPRISE_CATEGORY_TAXONOMY,
)
from app.domain.taxonomy.return_policies import (
    ReturnEligibilityResult,
    ReturnEligibilityEngine,
)

__all__ = [
    "CategoryPolicy",
    "CategoryTaxonomyService",
    "ENTERPRISE_CATEGORY_TAXONOMY",
    "ReturnEligibilityResult",
    "ReturnEligibilityEngine",
]
