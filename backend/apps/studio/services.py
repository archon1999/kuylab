from .content import REVISION, CATEGORIES, GOALS, all_items, localize
from .models import StudioAsset
from .comparisons import definitions as comparison_definitions
from .interactive import challenges
from .repertoire import SOURCES, SOURCE_BY_CODE
from .performance_variants import variant_definitions, default_variant_id
from .composition_showcase import presentation
from .library_taxonomy import taxonomy


class CatalogNotPrepared(Exception):
    pass


def public_definition(value):
    if isinstance(value, dict):
        return {key:public_definition(item) for key,item in value.items() if not key.startswith("_")}
    if isinstance(value, list):
        return [public_definition(item) for item in value]
    return value


def studio_catalog(language):
    # The catalog needs IDs and a few small metadata rows, not every study's
    # parsed note graph. JSON extraction works on both SQLite and PostgreSQL.
    assets = dict(StudioAsset.objects.values_list("key", "score_id"))
    source_keys = [source.asset_key for source in SOURCES]
    source_keys += [variant["_asset_key"] for source in SOURCES for variant in variant_definitions(source.code)]
    originals = {row["key"]: row for row in StudioAsset.objects.filter(key__in=source_keys).values(
        "key", "score_id", "score__arrangement__composition_id", "score__arrangement__composition__title",
        "score__arrangement__composition__composer", "score__parsed__metadata__duration_seconds")}
    definitions = all_items()
    required = [item["id"] for item in definitions if not item.get("stages")]
    required += [stage["_asset_key"] for item in definitions for stage in item.get("stages", [])]
    required += [variant["_asset_key"] for source in SOURCES for variant in variant_definitions(source.code)]
    if any(source.asset_key not in originals for source in SOURCES) or any(key not in assets for key in required):
        raise CatalogNotPrepared("The curated studio has not been prepared. Run seed_studio locally.")
    groups = {"lesson":[], "exercise":[], "theory":[], "journey":[]}
    for definition in definitions:
        item = localize(public_definition(definition),language)
        item["score_id"] = assets.get(item["id"])
        if item["kind"] in {"lesson", "journey"}:
            source = SOURCE_BY_CODE[definition.get("_composition", "still")]
            item["composition_id"] = originals[source.asset_key]["score__arrangement__composition_id"]
            for stage, source_stage in zip(item["stages"], definition["stages"]):
                stage["score_id"] = assets[source_stage["_asset_key"]]
            item["score_id"] = item["stages"][0]["score_id"]
        if item["kind"] == "theory":
            item["challenges"] = localize(challenges(definition["_generator"]["topic"]), language)
            item["comparisons"] = [{**localize(value, language), "score_id": assets[value["id"]]} for value in comparison_definitions(definition["_generator"]["topic"]) if value["id"] in assets]
        groups[item["kind"]].append(item)
    compositions = []
    for source in SOURCES:
        original = originals[source.asset_key]
        composition_id = original["score__arrangement__composition_id"]
        compositions.append({
            **presentation(source.code),
            **localize(taxonomy(source.code), language),
            "id":composition_id,"slug":source.slug,"title":original["score__arrangement__composition__title"],
            "subtitle":source.collection,
            "composer":original["score__arrangement__composition__composer"],"score_id":original["score_id"],
            "duration_seconds":original["score__parsed__metadata__duration_seconds"],
            "lesson_ids":[item["id"] for item in groups["lesson"] if item["composition_id"] == composition_id],
        })
        variants = variant_definitions(source.code)
        if variants:
            compositions[-1]["variants"] = [
                {**presentation(source.code, value["id"]), "id": value["id"], "title": localize(value["title"], language),
                 "description": localize(value["description"], language),
                 "score_id": assets[value["_asset_key"]],
                 "duration_seconds": originals[value["_asset_key"]]["score__parsed__metadata__duration_seconds"]}
                for value in variants
            ]
            preferred = next(value for value in variants if value["id"] == default_variant_id(source.code, variants))
            compositions[-1]["default_variant_id"] = preferred["id"]
            compositions[-1]["readable_holds"] = source.code == "all-in"
            compositions[-1]["score_id"] = assets[preferred["_asset_key"]]
    result = {"revision":REVISION,"compositions":compositions,"lessons":groups["lesson"],"exercises":groups["exercise"],"theory":groups["theory"],
        "journeys":groups["journey"],
        "categories":[{"id":key,"label":localize(label,language)} for key,label in CATEGORIES],
        "goals":[{"id":key,"label":localize(label,language)} for key,label in GOALS]}
    return result
