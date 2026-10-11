from datetime import timedelta
from django.utils import timezone
from .curriculum import DIAGNOSTIC_QUESTIONS, SKILLS, ensure_curriculum
from .models import DiagnosticAttempt, LessonProgress

QUIZ_PASS_SCORE = 80


def evaluate_diagnostic(answers, questions=None):
    raw = {key: {"knowledge": [], "self_reported": []} for key in SKILLS}
    feedback = []
    for question in questions if questions is not None else DIAGNOSTIC_QUESTIONS:
        answer = answers[question["id"]]
        if question["kind"] == "knowledge":
            correct = answer == question["correct_choice"]
            raw[question["skill"]]["knowledge"].append(100 if correct else 0)
            feedback.append({"id": question["id"], "correct": correct, "correct_choice": question["correct_choice"], "explanation": question["explanation"]})
        elif answer != "0":
            raw[question["skill"]]["self_reported"].append(round((int(answer) - 1) / 3 * 100))
    scores = {}
    for skill, values in raw.items():
        knowledge = round(sum(values["knowledge"]) / len(values["knowledge"])) if values["knowledge"] else None
        reported = round(sum(values["self_reported"]) / len(values["self_reported"])) if values["self_reported"] else None
        known = [value for value in [knowledge, reported] if value is not None]
        scores[skill] = {"knowledge_score": knowledge, "self_reported_score": reported,
                         "score": min(known) if known else None,
                         "evidence": "diagnostic_answers_and_self_report" if knowledge is not None and reported is not None else "diagnostic_answers" if knowledge is not None else "self_reported" if reported is not None else "not_assessed"}
    return scores, feedback


def progress_data(progress=None, now=None):
    now = now or timezone.now()
    if progress is None:
        return {"quiz_score": None, "quiz_passed": False, "drill_completed": False, "successful_repetitions": 0,
                "comfort": None, "bpm": None, "reflection": "", "review_due_at": None, "review_count": 0,
                "status": "not_started", "evidence": "not_assessed", "last_practice_at": None, "last_quiz_at": None}
    passed = progress.quiz_score is not None and progress.quiz_score >= QUIZ_PASS_SCORE
    drill = progress.successful_repetitions >= 3 and progress.comfort is not None and progress.comfort >= 4
    if progress.review_due_at and progress.review_due_at <= now:
        state = "review_due"
    elif passed and drill:
        state = "retained" if progress.review_count else "ready_for_review"
    else:
        state = "learning"
    return {"quiz_score": progress.quiz_score, "quiz_passed": passed, "drill_completed": drill,
            "successful_repetitions": progress.successful_repetitions, "comfort": progress.comfort,
            "bpm": progress.bpm, "reflection": progress.reflection,
            "review_due_at": progress.review_due_at, "review_count": progress.review_count,
            "status": state, "evidence": "quiz_and_self_report" if progress.last_practice_at and progress.last_quiz_at else "self_reported" if progress.last_practice_at else "quiz_answers",
            "last_practice_at": progress.last_practice_at, "last_quiz_at": progress.last_quiz_at}


def schedule_initial_review(progress, now):
    if progress.quiz_score is not None and progress.quiz_score >= QUIZ_PASS_SCORE and progress.successful_repetitions >= 3 and (progress.comfort or 0) >= 4 and progress.review_due_at is None:
        progress.review_due_at = now + timedelta(days=2)


def skill_profile(arrangement, profile, lessons=None):
    lessons = list(lessons if lessons is not None else ensure_curriculum(arrangement))
    latest = DiagnosticAttempt.objects.filter(arrangement=arrangement, profile=profile).order_by("-created_at", "-id").first()
    records = {record.lesson_id: record for record in LessonProgress.objects.filter(profile=profile, lesson__in=lessons)}
    skills = []
    for key, label in SKILLS.items():
        values = (latest.skill_scores.get(key, {}) if latest else {}).copy()
        knowledge = values.get("knowledge_score")
        reported = values.get("self_reported_score")
        current = [records[lesson.id] for lesson in lessons if lesson.skill == key and lesson.id in records]
        quiz_scores = [record.quiz_score for record in current if record.quiz_score is not None]
        practice_scores = [round(record.successful_repetitions / 3 * 100) if (record.comfort or 0) >= 4 else min(50, round(record.successful_repetitions / 3 * 100)) for record in current if record.last_practice_at]
        if quiz_scores:
            knowledge = round(sum(quiz_scores) / len(quiz_scores))
        if practice_scores:
            reported = min(practice_scores)
        known = [score for score in [knowledge, reported] if score is not None]
        skills.append({"id": key, "label": label, "score": min(known) if known else None,
                       "knowledge_score": knowledge, "self_reported_score": reported,
                       "evidence": "lesson_quiz_and_self_report" if quiz_scores and practice_scores else "lesson_quiz" if quiz_scores else "lesson_self_report" if practice_scores else values.get("evidence", "not_assessed")})
    return skills


def allocate_minutes(total, weights):
    """Positive integer slots; largest remainder preserves the exact budget."""
    count = len(weights)
    if total < count or not count:
        raise ValueError("Minute budget must cover every slot.")
    remaining = total - count
    quota = [remaining * weight / sum(weights) for weight in weights]
    result = [1 + int(value) for value in quota]
    remainder = total - sum(result)
    for index in sorted(range(count), key=lambda index: (-(quota[index] - int(quota[index])), index))[:remainder]:
        result[index] += 1
    return result


def source_notice(arrangement, lessons=None):
    lessons = list(lessons if lessons is not None else ensure_curriculum(arrangement))
    bound = next((lesson for lesson in lessons if lesson.score_version_id), None)
    if bound:
        if bound.content.get("exercise", {}).get("type") == "midi_source_fragment":
            return "MIDI player darsdan alohida. Har dars aynan shu fayldagi tovushlar va vaqt bo'lagiga bog'langan."
        return "Darslar import qilingan shu nota versiyasining metadata belgilari bilan bog'langan. Original mashq ijrosi asar ijrosidan alohida; takt bo'yicha texnik tahlil o'qituvchi tomonidan tasdiqlanmagan."
    if arrangement.full_score_verified_at:
        return "Shu to'liq 4 sahifali nota bilan ishlaymiz: 1–103 takt. Original tayyorlovdan so'ng kompozitsiyaga qaytamiz."
    if any(lesson.kind == "preparation" for lesson in lessons):
        return "Tanlangan nashrning tonallik/metr metadata belgilariga tayyorlov. To'liq nota yo'q: asar taktlarini, notalarini yoki barmoqlashini taxmin qilmaymiz."
    return "Aniq trek/aranjirovka va nota hali belgilanmagan. Bu holatda asarga tonallik yoki o'lchov biriktirilmaydi."


def adaptive_plan(arrangement, profile, minutes=None):
    minutes = minutes if minutes is not None else profile.practice_minutes
    lessons = list(ensure_curriculum(arrangement))
    now = timezone.now()
    skills = {item["id"]: item for item in skill_profile(arrangement, profile, lessons)}
    records = {record.lesson_id: record for record in LessonProgress.objects.filter(profile=profile, lesson__in=lessons)}
    notice = source_notice(arrangement, lessons)
    if not lessons or all(lesson.kind == "source" for lesson in lessons):
        slot = lessons[0] if lessons else None
        planned = min(minutes, 10)
        source_minutes, reflection_minutes = allocate_minutes(planned, [4, 1])
        return {"minutes": planned, "requested_minutes": minutes, "composition_id": arrangement.composition_id,
                "arrangement_id": arrangement.id, "source_notice": notice, "basis": "source_pending",
                "items": [{"kind": "lesson", "lesson_id": slot.id if slot else None, "title": slot.title if slot else "Variantni tanlang", "minutes": source_minutes, "reason": "Aniq nota ma'lum bo'lmagani uchun kompozitsiya darsini taxmin qilib tuzmaymiz."},
                          {"kind": "reflect", "lesson_id": None, "title": "Bir maqsadni yozing", "minutes": reflection_minutes, "reason": "Keyingi variant/nota tanlash uchun bitta aniq niyat."}]}
    ranked = []
    for lesson in lessons:
        state = progress_data(records.get(lesson.id), now)
        score = skills[lesson.skill]["score"]
        deficit = 50 if score is None else 100 - score
        due = state["status"] == "review_due"
        need_theory = not state["quiz_passed"]
        need_drill = not state["drill_completed"]
        priority = (300 if due else 0) + deficit + (40 if need_theory else 0) + (30 if need_drill else 0)
        if lesson.kind == "source_excerpt":
            priority += 120
        if state["status"] in ["ready_for_review", "retained"]:
            priority -= 100
        # Rhythm is a preparation dependency of the original two-hand drill.
        if lesson.skill == "coordination" and (skills["rhythm"]["score"] is None or skills["rhythm"]["score"] < 50):
            priority -= 50
        reason = "Rejalashtirilgan kechiktirilgan qayta sinov vaqti keldi." if due else f"{skills[lesson.skill]['label']}: " + ("hali tekshirilmagan; qisqa sinov bilan boshlaymiz." if score is None else f"oxirgi javob/kuzatuv {score}/100; bu ijro aniqligi balli emas.")
        if lesson.kind == "source_excerpt" and not due:
            reason = "Asosiy maqsad siz tanlagan kompozitsiya: avval importdagi haqiqiy parcha va uning yozilgan naqshini tekshiramiz. " + reason
        if not due and not need_theory and need_drill:
            reason += " Nazariya javobi bor, amaliy mashq hali tasdiqlanmagan."
        ranked.append((priority, lesson.order, lesson, reason, due))
    ranked.sort(key=lambda item: (-item[0], item[1]))
    count = 1 if minutes < 18 else 2
    selected = ranked[:count]
    reflection = 1 if minutes < 10 else 2
    break_minutes = 2 if minutes >= 40 else 0
    transferable = max(1, round((minutes - reflection - break_minutes) * 0.45))
    lesson_budget = minutes - reflection - break_minutes - transferable
    allocations = allocate_minutes(lesson_budget, [max(1, item[0] + 120) for item in selected])
    items = [{"kind": "review" if due else "lesson", "lesson_id": item.id, "title": item.title, "minutes": allocated, "reason": reason,
              "score_version_id": item.score_version_id, "practice_link": item.content.get("practice_link")}
             for (_, _, item, reason, due), allocated in zip(selected, allocations)]
    if break_minutes:
        items.append({"kind": "break", "lesson_id": None, "title": "Qisqa tanaffus", "minutes": break_minutes, "reason": "Qulaylikni qayta tekshiring."})
    first = selected[0][2]
    items.append({"kind": "transfer", "lesson_id": first.id, "title": "Asarga qayting", "minutes": transferable,
                  "reason": first.content.get("transfer", "O'zingiz tanlagan parchaga qayting."), "practice_link": first.content.get("practice_link"), "score_version_id": first.score_version_id})
    items.append({"kind": "reflect", "lesson_id": None, "title": "Natija va keyingi sinov", "minutes": reflection, "reason": "Bitta joy, qulay temp va keyingi urinish maqsadini qayd eting."})
    return {"minutes": minutes, "requested_minutes": minutes, "composition_id": arrangement.composition_id, "arrangement_id": arrangement.id,
            "source_notice": notice, "basis": "diagnostic_and_latest_lesson_evidence", "items": items,
            "rules": {"quiz_pass_score": QUIZ_PASS_SCORE, "initial_review_days": 2, "review_is_performance_and_quiz": True, "song_mastery_inferred": False}}
