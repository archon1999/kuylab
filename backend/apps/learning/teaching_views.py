from datetime import timedelta
from copy import deepcopy
import hashlib
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.http import FileResponse, Http404
from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .adaptive import QUIZ_PASS_SCORE, adaptive_plan, evaluate_diagnostic, progress_data, schedule_initial_review, skill_profile, source_notice
from .curriculum import diagnostic_definitions, diagnostic_questions, ensure_curriculum, score_binding
from .models import Arrangement, Composition, DiagnosticAttempt, LearningLesson, LessonPracticeAttempt, LessonProgress, QuizAttempt
from .serializers import ArrangementSerializer
from .teaching_serializers import AnswersSerializer, LessonPracticeSerializer, PlanMinutesSerializer
from .views import local_profile
from .exercises import authored_hands, drill_xml
from .localization import localized_diagnostic, localized_diagnostic_feedback, localized_lesson, localized_plan, localized_question, localized_skills, request_language


def selected_arrangement(request, pk):
    composition = get_object_or_404(Composition, pk=pk)
    selected = request.query_params.get("arrangement_id")
    if selected is not None:
        try:
            selected = int(selected)
        except (TypeError, ValueError, OverflowError):
            return None
        if selected < 1 or selected > 2**63 - 1:
            return None
        return get_object_or_404(Arrangement, pk=selected, composition=composition)
    arrangement = Arrangement.objects.filter(composition=composition).first()
    if arrangement is None:
        raise Http404
    return arrangement


def translated_plan(arrangement, learner, lang, minutes=None):
    return localized_plan(adaptive_plan(arrangement, learner, minutes), list(ensure_curriculum(arrangement)), lang)


def public_lesson(lesson, profile, lang="uz"):
    record = LessonProgress.objects.filter(profile=profile, lesson=lesson).first()
    questions = [{"id": question["id"], "prompt": question["prompt"], "choices": question["choices"]} for question in lesson.quiz.get("questions", [])]
    exercise = {**lesson.content.get("exercise", {})}
    if exercise.get("notes") or exercise.get("chords"):
        exercise["score_url"] = f"/api/lessons/{lesson.id}/exercise/"
        exercise["musicxml_url"] = f"/api/lessons/{lesson.id}/exercise/musicxml/"
    if exercise.get("type") == "midi_source_fragment":
        exercise["fragment_url"] = f"/api/lessons/{lesson.id}/exercise/"
        exercise["score_url"] = exercise["fragment_url"]
    data = {"id": lesson.id, "arrangement_id": lesson.arrangement_id, "composition_id": lesson.arrangement.composition_id,
            "code": lesson.code, "title": lesson.title, "skill": lesson.skill, "summary": lesson.summary,
            "minutes": lesson.minutes, "context": lesson.context, "kind": lesson.kind, "content_version": lesson.content_version,
            "explanation": lesson.content.get("explanation", []), "steps": lesson.content.get("steps", []),
            "exercise": exercise, "transfer": lesson.content.get("transfer", ""), "sources": lesson.content.get("sources", []),
            "success_criterion": lesson.success_criterion, "quiz": {"questions": questions}, "progress": progress_data(record),
            "score_version_id": lesson.score_version_id, "score_binding": lesson.content.get("score_binding"),
            "practice_link": lesson.content.get("practice_link"), "source_analysis": lesson.content.get("source_analysis")}
    return localized_lesson(data, lesson, lang)


@api_view(["GET"])
def curriculum(request, pk):
    arrangement = selected_arrangement(request, pk)
    if arrangement is None:
        return Response({"arrangement_id": "Butun son kiriting."}, status=400)
    learner = local_profile(request)
    lang = request_language(request, learner)
    lessons = list(ensure_curriculum(arrangement))
    attempt = learner.diagnostics.filter(arrangement=arrangement).order_by("-created_at", "-id").first()
    notice = source_notice(arrangement, lessons)
    if lang != "uz":
        midi_course = any(lesson.content.get("exercise", {}).get("type") == "midi_source_fragment" for lesson in lessons)
        if midi_course:
            notice = "The MIDI player is separate; each lesson uses exact source notes and timestamps." if lang == "en" else "MIDI-плеер открыт отдельно; уроки используют точные звуки и время источника."
        elif any(lesson.score_version_id for lesson in lessons):
            notice = "Teaching follows the exact imported score and its written evidence." if lang == "en" else "Уроки следуют точным импортированным нотам и их записанным данным."
        elif arrangement.full_score_verified_at:
            notice = "The complete selected score is available; return to the actual composition after original preparation." if lang == "en" else "Полные выбранные ноты доступны; после оригинальной подготовки вернитесь к произведению."
        else:
            notice = "Choose the complete exact source to begin composition lessons." if lang == "en" else "Выберите полный точный источник перед уроками по произведению."
    return Response({"language": lang, "composition_id": pk, "arrangement_id": arrangement.id, "arrangement": ArrangementSerializer(arrangement, context={"language": lang}).data,
                     "readiness": "composition_ready" if any(lesson.content.get("exercise", {}).get("type") == "midi_source_fragment" for lesson in lessons) else "preparation" if any(lesson.kind == "preparation" for lesson in lessons) else "source_pending",
                     "source_notice": notice, "score_binding": score_binding(arrangement),
                     "skills": localized_skills(skill_profile(arrangement, learner, lessons), lang),
                     "diagnostic": {"questions": localized_diagnostic(diagnostic_questions(diagnostic_definitions(arrangement)), lang), "latest_attempt": {"id": attempt.id, "answers": attempt.answers, "skills": attempt.skill_scores, "feedback": localized_diagnostic_feedback(attempt.feedback, lang), "created_at": attempt.created_at} if attempt else None},
                     "lessons": [public_lesson(lesson, learner, lang) for lesson in lessons], "adaptive_plan": translated_plan(arrangement, learner, lang)})


@api_view(["POST"])
def diagnostic(request, pk):
    arrangement = selected_arrangement(request, pk)
    if arrangement is None:
        return Response({"arrangement_id": "Butun son kiriting."}, status=400)
    learner = local_profile(request)
    lang = request_language(request, learner)
    questions = diagnostic_definitions(arrangement)
    serializer = AnswersSerializer(data=request.data, context={"questions": questions})
    serializer.is_valid(raise_exception=True)
    answers = serializer.validated_data["answers"]
    scores, feedback = evaluate_diagnostic(answers, questions)
    attempt = DiagnosticAttempt.objects.create(profile=learner, arrangement=arrangement, answers=answers, skill_scores=scores, feedback=feedback)
    return Response({"language": lang, "id": attempt.id, "arrangement_id": arrangement.id, "skills": localized_skills(skill_profile(arrangement, learner), lang), "feedback": localized_diagnostic_feedback(feedback, lang),
                     "created_at": attempt.created_at, "adaptive_plan": translated_plan(arrangement, learner, lang)}, status=201)


@api_view(["GET"])
def lesson_detail(request, pk):
    lesson = get_object_or_404(LearningLesson.objects.select_related("arrangement"), pk=pk)
    learner = local_profile(request)
    return Response(public_lesson(lesson, learner, request_language(request, learner)))


@api_view(["POST"])
def lesson_quiz(request, pk):
    lesson = get_object_or_404(LearningLesson.objects.select_related("arrangement"), pk=pk)
    learner = local_profile(request)
    lang = request_language(request, learner)
    questions = lesson.quiz.get("questions", [])
    if not questions:
        return Response({"detail": "Bu dars manba tanlash vazifasi; quiz yo'q."}, status=400)
    serializer = AnswersSerializer(data=request.data, context={"questions": questions})
    serializer.is_valid(raise_exception=True)
    answers = serializer.validated_data["answers"]
    feedback = [{"id": question["id"], "correct": answers[question["id"]] == question["correct_choice"],
                 "correct_choice": question["correct_choice"], "explanation": question["explanation"]} for question in questions]
    score = round(sum(item["correct"] for item in feedback) / len(questions) * 100)
    now = timezone.now()
    with transaction.atomic():
        record, _ = LessonProgress.objects.select_for_update().get_or_create(profile=learner, lesson=lesson)
        record.quiz_score = score
        record.last_quiz_at = now
        if record.review_due_at and record.review_due_at <= now:
            record.review_quiz_passed_at = now if score >= QUIZ_PASS_SCORE else None
        schedule_initial_review(record, now)
        record.save()
        attempt = QuizAttempt.objects.create(profile=learner, lesson=lesson, answers=answers, score=score, feedback=feedback, content_version=lesson.content_version)
    translated_questions = {question["id"]: localized_question(question, lesson, lang) for question in questions}
    response_feedback = [{**item, "explanation": translated_questions[item["id"]]["explanation"]} for item in feedback]
    return Response({"language": lang, "id": attempt.id, "score": score, "passed": score >= QUIZ_PASS_SCORE, "feedback": response_feedback,
                     "progress": progress_data(record), "adaptive_plan": translated_plan(lesson.arrangement, learner, lang)}, status=201)


@api_view(["POST"])
def lesson_practice(request, pk):
    lesson = get_object_or_404(LearningLesson.objects.select_related("arrangement"), pk=pk)
    learner = local_profile(request)
    lang = request_language(request, learner)
    serializer = LessonPracticeSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    fields = serializer.validated_data
    now = timezone.now()
    with transaction.atomic():
        record, _ = LessonProgress.objects.select_for_update().get_or_create(profile=learner, lesson=lesson)
        for field, value in fields.items():
            setattr(record, field, value)
        record.last_practice_at = now
        if record.review_due_at and record.review_due_at <= now and record.review_quiz_passed_at and record.review_quiz_passed_at >= record.review_due_at and record.quiz_score is not None and record.quiz_score >= QUIZ_PASS_SCORE and fields["successful_repetitions"] >= 3 and fields["comfort"] >= 4:
            record.review_count += 1
            record.review_due_at = now + timedelta(days=min(28, 7 * record.review_count))
            record.review_quiz_passed_at = None
        schedule_initial_review(record, now)
        record.save()
        attempt = LessonPracticeAttempt.objects.create(profile=learner, lesson=lesson, **fields)
    return Response({"language": lang, "id": attempt.id, "evidence": "self_reported", "progress": progress_data(record),
                     "adaptive_plan": translated_plan(lesson.arrangement, learner, lang)}, status=201)


@api_view(["GET", "POST"])
def recommendation(request, pk):
    arrangement = selected_arrangement(request, pk)
    if arrangement is None:
        return Response({"arrangement_id": "Butun son kiriting."}, status=400)
    data = request.data if request.method == "POST" else {"minutes": request.query_params["minutes"]} if "minutes" in request.query_params else {}
    serializer = PlanMinutesSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    learner = local_profile(request)
    return Response(translated_plan(arrangement, learner, request_language(request, learner), serializer.validated_data.get("minutes")))


@api_view(["GET"])
def lesson_exercise(request, pk):
    from apps.scores.parser import parse_musicxml
    lesson = get_object_or_404(LearningLesson.objects.select_related("arrangement"), pk=pk)
    exercise = lesson.content.get("exercise", {})
    if exercise.get("type") == "midi_source_fragment":
        from apps.scores.models import Score
        from apps.scores.serializers import ScoreSerializer
        source = get_object_or_404(Score, pk=lesson.score_version_id, arrangement=lesson.arrangement, file_format="midi")
        response = dict(ScoreSerializer(source).data)
        parsed = deepcopy(source.parsed)
        start_q, end_q = exercise["start_quarters"], exercise["end_quarters"]
        start_s, end_s = exercise["start_seconds"], exercise["end_seconds"]
        wanted = set(exercise["event_ids"])
        selected = [event for event in parsed["events"] if event["id"] in wanted]
        ticks_per_quarter = parsed["metadata"]["ticks_per_beat"]
        clipped_windows = []
        for window in parsed["measures"]:
            clipped_start = max(window["start_quarters"], start_q)
            clipped_end = min(window["start_quarters"] + window["length_quarters"], end_q)
            if clipped_end <= clipped_start + 1e-9:
                continue
            clipped_windows.append({**window, "index": len(clipped_windows), "source_measure_index": window["index"],
                "start_quarters": clipped_start - start_q, "length_quarters": clipped_end - clipped_start,
                "start_seconds": (start_s if clipped_start == start_q else window["start_seconds"]) - start_s,
                "end_seconds": (end_s if clipped_end == end_q else window["end_seconds"]) - start_s,
                "meter_offset_quarters": clipped_start - window["start_quarters"],
                "tempos": [{**tempo, "offset_quarters": tempo["onset_quarters"] - clipped_start} for tempo in parsed["tempo_map"] if clipped_start <= tempo["onset_quarters"] < clipped_end],
                "provenance": "actual_midi_fragment_navigation_window"})
        windows_by_source = {window["source_measure_index"]: window for window in clipped_windows}
        for event in selected:
            event["source_onset_quarters"] = event["onset_quarters"]
            event["source_onset_seconds"] = event["onset_seconds"]
            event["source_measure_index"] = event["measure_index"]
            for field in ["duration_quarters", "duration_seconds", "sound_duration_quarters", "sound_duration_seconds"]:
                event[f"source_{field}"] = event[field]
            event["onset_quarters"] -= start_q
            event["onset_seconds"] -= start_s
            event["duration_quarters"] = min(event["duration_quarters"], end_q - start_q - event["onset_quarters"])
            event["duration_seconds"] = min(event["duration_seconds"], end_s - start_s - event["onset_seconds"])
            event["sound_duration_quarters"] = min(event["sound_duration_quarters"], end_q - start_q - event["onset_quarters"])
            event["sound_duration_seconds"] = min(event["sound_duration_seconds"], end_s - start_s - event["onset_seconds"])
            window = windows_by_source[event["source_measure_index"]]
            event["measure_index"] = window["index"]
            event["measure_number"] = window["number"]
            event["offset_quarters"] = event["onset_quarters"] - window["start_quarters"]
            for field in ["start_ticks", "end_ticks", "sound_end_ticks"]:
                event[f"source_{field}"] = event[field]
            event["start_ticks"] = round(event["onset_quarters"] * ticks_per_quarter)
            event["end_ticks"] = round((event["onset_quarters"] + event["duration_quarters"]) * ticks_per_quarter)
            event["sound_end_ticks"] = round((event["onset_quarters"] + event["sound_duration_quarters"]) * ticks_per_quarter)
        tempo_at_start = next((entry for entry in reversed(parsed["tempo_map"]) if entry["onset_quarters"] <= start_q), parsed["tempo_map"][0])
        parsed["tempo_map"] = [{**tempo_at_start, "source_onset_ticks": tempo_at_start["onset_ticks"], "onset_ticks": 0, "onset_quarters": 0, "onset_seconds": 0}, *[{**entry, "source_onset_ticks": entry["onset_ticks"], "onset_ticks": round((entry["onset_quarters"] - start_q) * ticks_per_quarter), "onset_quarters": entry["onset_quarters"] - start_q, "onset_seconds": entry["onset_seconds"] - start_s} for entry in parsed["tempo_map"] if start_q < entry["onset_quarters"] < end_q]]
        parsed["events"] = selected
        parsed["parts"] = [{**part, "note_count": sum(event["part_id"] == part["id"] for event in selected)} for part in parsed["parts"] if any(event["part_id"] == part["id"] for event in selected)]
        parsed["measures"] = clipped_windows
        parsed["playback_order"] = list(range(len(clipped_windows)))
        parsed["metadata"].update({"measure_count": len(clipped_windows), "event_count": len(selected), "total_quarters": end_q - start_q, "duration_seconds": end_s - start_s, "source_fragment": True,
                                   "source_file_end_ticks": parsed["metadata"]["file_end_ticks"], "file_end_ticks": round((end_q - start_q) * ticks_per_quarter),
                                   "pitch_range": {"min": min(event["pitch"]["midi"] for event in selected), "max": max(event["pitch"]["midi"] for event in selected)}})
        parsed["fragment"] = {"source_score_id": source.id, "source_sha256": source.content_sha256, "start_seconds": start_s, "end_seconds": end_s, "start_quarters": start_q, "end_quarters": end_q, "event_ids": exercise["event_ids"]}
        for field in ["pedal_events", "control_events"]:
            parsed[field] = [{**event, "source_onset_ticks": event["onset_ticks"], "onset_ticks": round((event["onset_quarters"] - start_q) * ticks_per_quarter), "onset_seconds": event["onset_seconds"] - start_s, "onset_quarters": event["onset_quarters"] - start_q} for event in parsed[field] if start_s <= event["onset_seconds"] < end_s]
        parsed["metadata"]["part_count"] = len(parsed["parts"])
        parsed["metadata"]["tempo"] = {**parsed["metadata"]["tempo"], "quarter_bpm": tempo_at_start["quarter_bpm"], "bpm": tempo_at_start["quarter_bpm"]}
        for map_field, metadata_field in [("time_signature_map", "time"), ("key_signature_map", "key")]:
            entries = parsed[map_field]
            current = next((entry for entry in reversed(entries) if entry["onset_quarters"] <= start_q), None)
            parsed[map_field] = ([{**current, "onset_quarters": 0, "onset_ticks": 0}] if current else []) + [
                {**entry, "onset_quarters": entry["onset_quarters"] - start_q, "onset_ticks": round((entry["onset_quarters"] - start_q) * ticks_per_quarter)}
                for entry in entries if start_q < entry["onset_quarters"] < end_q]
            parsed["metadata"][metadata_field] = {key: value for key, value in current.items() if key not in ["onset_ticks", "onset_quarters"]} if current else None
        learner = local_profile(request)
        title = public_lesson(lesson, learner, request_language(request, learner))["title"]
        response.update({"id": f"lesson-{lesson.id}", "lesson_id": lesson.id, "source_score_id": source.id, "parsed": parsed, "metadata": parsed["metadata"], "fragment": parsed["fragment"], "musicxml_url": "", "title": title,
                         "sections": [], "hand_overrides": {event_id: hand for event_id, hand in source.hand_overrides.items() if event_id in wanted}})
        return Response(response)
    try:
        xml = drill_xml(lesson)
    except ValueError as error:
        return Response({"detail": str(error)}, status=404)
    parsed = parse_musicxml(xml)
    known_hands = authored_hands(lesson)
    hands = {event["id"]: event["hand"] if event["hand"] in ["right", "left"] else known_hands[0] for event in parsed["events"] if not event["rest"]}
    return Response({"id": f"lesson-{lesson.id}", "lesson_id": lesson.id, "arrangement_id": lesson.arrangement_id,
                     "version": lesson.content_version, "title": f"Original · {lesson.title}", "is_demo": True,
                     "original_filename": f"lesson-{lesson.id}.musicxml", "content_sha256": hashlib.sha256(xml).hexdigest(),
                     "metadata": parsed["metadata"], "parsed": parsed, "musicxml_url": f"/api/lessons/{lesson.id}/exercise/musicxml/",
                     "rights_basis": "original_cc0", "rights_note": "KuyLab uchun yozilgan original mashq (CC0). Tanlangan kompozitsiyadan ko'chirilmagan.",
                     "exact_version_confirmed": False, "hand_overrides": hands, "sections": [], "created_at": None, "rights_confirmed_at": None})


@api_view(["GET"])
def lesson_exercise_musicxml(request, pk):
    from apps.scores.views import xml_response
    lesson = get_object_or_404(LearningLesson, pk=pk)
    try:
        return xml_response(drill_xml(lesson))
    except ValueError as error:
        return Response({"detail": str(error)}, status=404)


@api_view(["GET"])
def arrangement_full_score(request, pk):
    from .full_scores import verified_pdf_path
    arrangement = get_object_or_404(Arrangement, pk=pk)
    path = verified_pdf_path(arrangement)
    if path is None:
        return Response({"detail": "Verified complete PDF is unavailable."}, status=404)
    source = path.open("rb")
    response = FileResponse(source, content_type="application/pdf", as_attachment=False, filename="full-piano-score.pdf")
    response["X-Content-Type-Options"] = "nosniff"
    response["Cache-Control"] = "private, no-store"
    response["X-Frame-Options"] = "SAMEORIGIN"
    response["Content-Security-Policy"] = "frame-ancestors 'self'"
    return response


@api_view(["GET"])
def arrangement_full_score_page(request, pk, page):
    from .full_scores import verified_page_paths
    arrangement = get_object_or_404(Arrangement, pk=pk)
    pages = verified_page_paths(arrangement)
    if page < 1 or page > len(pages):
        raise Http404
    response = FileResponse(pages[page - 1].open("rb"), content_type="image/png")
    response["X-Content-Type-Options"] = "nosniff"
    response["Cache-Control"] = "private, no-store"
    return response
