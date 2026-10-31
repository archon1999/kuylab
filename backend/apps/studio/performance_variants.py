"""One arrangement-variant contract for supplied packages and performances."""
from .all_in_package import variant_definitions as package_variants
from .ivory_repertoire import GROUP_BY_CODE, variant_definitions as ivory_variants


def variant_definitions(code):
    return ivory_variants(code) if code in GROUP_BY_CODE else package_variants(code)


def default_variant_id(code, variants=None):
    values = variant_definitions(code) if variants is None else variants
    # The standard All in performance is Full/Hard; Easy remains an explicit choice.
    return "hard" if code == "all-in" else values[0]["id"] if values else None
