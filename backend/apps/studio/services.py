from .content import REVISION, CATEGORIES, GOALS, all_items, localize, tr
from .models import StudioAsset
from .comparisons import definitions as comparison_definitions
from .interactive import challenges


class CatalogNotPrepared(Exception):
    pass


def public_definition(value):
    if isinstance(value, dict):
        return {key:public_definition(item) for key,item in value.items() if not key.startswith("_")}
    if isinstance(value, list):
        return [public_definition(item) for item in value]
    return value


def studio_catalog(language):
    assets = {asset.key:asset.score for asset in StudioAsset.objects.select_related("score__arrangement__composition")}
    original = assets.get("composition:still:original")
    definitions = all_items()
    required = [item["id"] for item in definitions]
    required += [stage["_asset_key"] for item in definitions for stage in item.get("stages", [])]
    if original is None or any(key not in assets for key in required):
        raise CatalogNotPrepared("The curated studio has not been prepared. Run seed_studio locally.")
    composition = original.arrangement.composition
    groups = {"lesson":[], "exercise":[], "theory":[], "journey":[]}
    for definition in definitions:
        item = localize(public_definition(definition),language)
        item["score_id"] = assets[item["id"]].pk
        if item["kind"] in {"lesson", "journey"}:
            item["composition_id"] = composition.pk
            for stage, source_stage in zip(item["stages"], definition["stages"]):
                stage["score_id"] = assets[source_stage["_asset_key"]].pk
            item["score_id"] = item["stages"][0]["score_id"]
        if item["kind"] == "theory":
            item["challenges"] = localize(challenges(definition["_generator"]["topic"]), language)
            item["comparisons"] = [{**localize(value, language), "score_id": assets[value["id"]].pk} for value in comparison_definitions(definition["_generator"]["topic"]) if value["id"] in assets]
        groups[item["kind"]].append(item)
    result = {"revision":REVISION,"compositions":[{
        "id":composition.pk,"slug":"winter-sonata-still","title":composition.title,
        "subtitle":localize(tr("Winter Sonata · siz tanlagan MIDI", "Winter Sonata · выбранный вами MIDI", "Winter Sonata · your selected MIDI"),language),
        "composer":"","score_id":original.pk,"duration_seconds":original.parsed["metadata"]["duration_seconds"],
        "lesson_ids":[item["id"] for item in groups["lesson"]],
    }],"lessons":groups["lesson"],"exercises":groups["exercise"],"theory":groups["theory"],
        "journeys":groups["journey"],
        "categories":[{"id":key,"label":localize(label,language)} for key,label in CATEGORIES],
        "goals":[{"id":key,"label":localize(label,language)} for key,label in GOALS]}
    return result
