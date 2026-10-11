import hashlib
from functools import lru_cache
from pathlib import Path, PurePosixPath
from django.core.files.base import ContentFile
from django.db import IntegrityError, OperationalError, transaction
from django.db.models import Max
from django.http import FileResponse, HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from apps.learning.models import Arrangement, Composition
from .models import Score
from .parser import ScoreImportError, extract_musicxml, parse_musicxml
from .midi import parse_midi
from .serializers import ImportSerializer, ScoreSerializer, ScoreSummarySerializer, ScoreUpdateSerializer

DEMO_PATH = Path(__file__).with_name("demo.musicxml")


@api_view(["GET", "POST"])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def scores(request):
    if request.method == "GET":
        items = Score.objects.select_related("arrangement").all()
        arrangement = request.query_params.get("arrangement_id")
        if arrangement:
            try:
                arrangement_id = int(arrangement)
                if not 1 <= arrangement_id <= 2 ** 63 - 1:
                    raise ValueError
                items = items.filter(arrangement_id=arrangement_id)
            except (TypeError, ValueError, OverflowError):
                return Response({"arrangement_id": "Butun son kiriting."}, status=400)
        return Response(ScoreSummarySerializer(items[:100], many=True).data)
    serializer = ImportSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    fields = serializer.validated_data
    uploaded = fields["file"]
    suffix = PurePosixPath(uploaded.name.replace("\\", "/")).suffix.lower()
    file_format = "midi" if suffix in [".mid", ".midi"] else "musicxml"
    try:
        # Do not trust UploadedFile.size alone (custom handlers may report it).
        from .parser import MAX_UPLOAD_BYTES
        content = uploaded.read(MAX_UPLOAD_BYTES + 1)
        if file_format == "midi":
            parsed = parse_midi(content, fields["title"] or PurePosixPath(uploaded.name).stem)
        else:
            content = extract_musicxml(content, uploaded.name)
            parsed = parse_musicxml(content)
    except ScoreImportError:
        return Response({"file": "The MIDI or MusicXML file could not be read. Check its format and size."}, status=status.HTTP_400_BAD_REQUEST)
    score = None
    def remove_failed_file():
        if score is not None and score.musicxml:
            try:
                score.musicxml.delete(save=False)
            except OSError:
                # Keep the original failure useful; a storage outage can also
                # prevent cleanup. No existing source file is ever targeted.
                pass
    try:
        with transaction.atomic():
            if "composition" in fields:
                composition = Composition.objects.select_for_update().get(pk=fields["composition"].pk)
                target = Arrangement.objects.filter(composition=composition).first()
                if target is None:
                    target = Arrangement.objects.create(composition=composition,
                        title=fields["title"] or parsed["metadata"]["title"][:180],
                        source_url=fields["source_url"], source_kind="link" if fields["source_url"] else "pending",
                        workflow_status="imported_midi" if file_format == "midi" else "imported_score",
                        exact_version_confirmed=fields["exact_version_confirmed"])
                arrangement = Arrangement.objects.select_for_update().get(pk=target.pk)
            else:
                arrangement = Arrangement.objects.select_for_update().get(pk=fields["arrangement"].pk)
            version = (Score.objects.filter(arrangement=arrangement).aggregate(last=Max("version"))["last"] or 0) + 1
            score = Score(arrangement=arrangement, version=version,
                file_format=file_format, source_url=fields["source_url"], source_provenance={"kind": "user_uploaded_file", "format": file_format},
                title=fields["title"] or parsed["metadata"]["title"][:180],
                original_filename=PurePosixPath(uploaded.name.replace("\\", "/")).name[:255],
                content_sha256=hashlib.sha256(content).hexdigest(), parsed=parsed,
                rights_note=fields["rights_note"], rights_confirmed_at=timezone.now(),
                exact_version_confirmed=fields["exact_version_confirmed"])
            score.musicxml.save("score.mid" if file_format == "midi" else "score.musicxml", ContentFile(content), save=False)
            score.save()
    except (IntegrityError, OperationalError):
        remove_failed_file()
        return Response({"detail": "The local database is busy. The import was not saved; try again."}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    except OSError:
        remove_failed_file()
        return Response({"file": "The local source file could not be saved. Check available disk space and file permissions."}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    except Exception:
        # Files are outside database transactions: remove only this failed import.
        remove_failed_file()
        raise
    return Response(ScoreSerializer(score).data, status=status.HTTP_201_CREATED)


@api_view(["GET", "PATCH"])
def score_detail(request, pk):
    score = get_object_or_404(Score, pk=pk)
    if request.method == "PATCH":
        serializer = ScoreUpdateSerializer(data=request.data, context={"score": score})
        serializer.is_valid(raise_exception=True)
        for field, value in serializer.validated_data.items():
            setattr(score, field, value)
        if serializer.validated_data:
            score.save(update_fields=list(serializer.validated_data))
    return Response(ScoreSerializer(score).data)


def xml_response(content):
    response = HttpResponse(content, content_type="application/vnd.recordare.musicxml+xml")
    response["X-Content-Type-Options"] = "nosniff"
    response["Content-Security-Policy"] = "default-src 'none'; sandbox"
    response["Cache-Control"] = "private, no-store"
    return response


@api_view(["GET"])
def score_musicxml(request, pk):
    score = get_object_or_404(Score, pk=pk)
    if score.file_format != "musicxml":
        return Response({"detail": "This source is MIDI; no notation was invented."}, status=404)
    try:
        with score.musicxml.open("rb") as source:
            content = source.read()
    except FileNotFoundError:
        return Response({"detail": "Nota fayli topilmadi."}, status=404)
    except OSError:
        return Response({"detail": "The local source file is temporarily unavailable."}, status=503)
    return xml_response(content)


@api_view(["GET"])
def score_file(request, pk):
    score = get_object_or_404(Score, pk=pk)
    try:
        source = score.musicxml.open("rb")
    except FileNotFoundError:
        return Response({"detail": "Source file is unavailable."}, status=404)
    except OSError:
        return Response({"detail": "The local source file is temporarily unavailable."}, status=503)
    response = FileResponse(source, content_type="audio/midi" if score.file_format == "midi" else "application/vnd.recordare.musicxml+xml", as_attachment=True, filename=score.original_filename)
    response["X-Content-Type-Options"] = "nosniff"
    response["Cache-Control"] = "private, no-store"
    return response


@lru_cache(maxsize=1)
def demo_parsed():
    return parse_musicxml(DEMO_PATH.read_bytes())


@api_view(["GET"])
def demo(request):
    parsed = demo_parsed()
    return Response({"id": "demo", "arrangement_id": None, "version": 1, "title": "Original 6/8 mashqi", "is_demo": True,
        "original_filename": "demo.musicxml", "content_sha256": hashlib.sha256(DEMO_PATH.read_bytes()).hexdigest(),
        "metadata": parsed["metadata"], "parsed": parsed, "musicxml_url": "/api/scores/demo/musicxml/",
        "rights_basis": "original_cc0", "rights_note": "KuyLab uchun yozilgan original mashq (CC0). He’s a Pirate yoki boshqa asardan ko'chirilmagan.",
        "exact_version_confirmed": False, "hand_overrides": {}, "sections": [], "created_at": None, "rights_confirmed_at": None})


@api_view(["GET"])
def demo_musicxml(request):
    return xml_response(DEMO_PATH.read_bytes())
