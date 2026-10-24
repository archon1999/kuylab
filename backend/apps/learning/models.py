from decimal import Decimal
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE, related_name="piano_profile")
    player_preferences = models.JSONField(default=dict)
    player_context_preferences = models.JSONField(default=dict)
    display_name = models.CharField(max_length=80, default="Pianinochi")
    instrument_model = models.CharField(max_length=120, default="Yamaha YDP-145")
    keys = models.PositiveSmallIntegerField(default=88, validators=[MinValueValidator(25), MaxValueValidator(128)])
    practice_minutes = models.PositiveSmallIntegerField(default=30, validators=[MinValueValidator(5), MaxValueValidator(180)])
    level = models.CharField(max_length=40, default="intermediate")
    goal = models.CharField(max_length=240, default="Sevimli asarlarimni ongli va ravon chalish")
    language = models.CharField(max_length=2, default="uz", choices=[("uz", "O'zbek"), ("ru", "Русский"), ("en", "English")])
    theme = models.CharField(max_length=5, default="light", choices=[("light", "Light"), ("dark", "Dark")])


class Composition(models.Model):
    seed_key = models.CharField(max_length=80, null=True, blank=True, unique=True, editable=False)
    title = models.CharField(max_length=160)
    composer = models.CharField(max_length=160, blank=True)
    category = models.CharField(max_length=80, default="Mening repertuarim")
    goal = models.CharField(max_length=240, blank=True)
    color = models.CharField(max_length=7, default="#D09B65")
    status = models.CharField(max_length=24, default="queued", choices=[
        ("active", "Faol"), ("queued", "Navbatda"), ("completed", "Yakunlangan"),
    ])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["id"]


class Arrangement(models.Model):
    seed_key = models.CharField(max_length=80, null=True, blank=True, unique=True, editable=False)
    is_default = models.BooleanField(default=True)
    composition = models.ForeignKey(Composition, on_delete=models.CASCADE, related_name="arrangements")
    title = models.CharField(max_length=180, default="Aniq variant hali tanlanmagan")
    source_url = models.URLField(max_length=1000, blank=True)
    reference_video_url = models.URLField(max_length=1000, blank=True)
    full_score_url = models.URLField(max_length=1000, blank=True)
    full_score_format = models.CharField(max_length=12, blank=True)
    full_score_verified_at = models.DateTimeField(null=True, blank=True)
    full_score_file = models.FileField(upload_to="arrangements/full_scores/", blank=True)
    source_kind = models.CharField(max_length=20, default="pending", choices=[
        ("pending", "Kutilmoqda"), ("link", "Havola"), ("own", "O'z ishlanmasi"),
        ("licensed", "Litsenziyalangan"), ("public_domain", "Public domain"),
    ])
    arranger = models.CharField(max_length=120, blank=True)
    rights_status = models.CharField(max_length=30, default="unconfirmed", choices=[
        ("unconfirmed", "Tekshirilmagan"), ("user_owned", "Foydalanuvchi nusxasi"),
        ("licensed", "Litsenziya tasdiqlangan"), ("public_domain", "Public domain tasdiqlangan"),
    ])
    rights_note = models.TextField(blank=True)
    exact_version_confirmed = models.BooleanField(default=False)
    workflow_status = models.CharField(max_length=40, default="needs_source")
    key_signature = models.CharField(max_length=40, blank=True)
    time_signature = models.CharField(max_length=20, blank=True)
    tempo_bpm = models.PositiveSmallIntegerField(null=True, blank=True)
    tempo_beat_unit = models.CharField(max_length=30, blank=True)
    page_count = models.PositiveSmallIntegerField(null=True, blank=True)
    # Complete reference files retain their source and license provenance.

    class Meta:
        ordering = ["-is_default", "id"]


class PracticePlan(models.Model):
    arrangement = models.OneToOneField(Arrangement, on_delete=models.CASCADE, related_name="plan")
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="plans")
    title = models.CharField(max_length=180)
    summary = models.TextField()
    readiness = models.CharField(max_length=24, default="needs_arrangement", choices=[
        ("needs_arrangement", "Variant kerak"), ("needs_score", "Nota nusxasi kerak"), ("needs_review", "Ustoz tekshiruvi kerak"),
        ("ready", "Tayyor"),
    ])
    is_demo = models.BooleanField(default=True)


class PracticeTask(models.Model):
    plan = models.ForeignKey(PracticePlan, on_delete=models.CASCADE, related_name="tasks")
    order = models.PositiveSmallIntegerField()
    kind = models.CharField(max_length=20, choices=[
        ("listen", "Tinglash"), ("theory", "Nazariya"), ("technique", "Texnika"),
        ("piece", "Kompozitsiya"), ("reflect", "Xulosa"),
    ])
    title = models.CharField(max_length=180)
    instructions = models.TextField()
    minutes = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(120)])
    concept = models.CharField(max_length=120, blank=True)
    success_criterion = models.CharField(max_length=280)
    completed = models.BooleanField(default=False)

    class Meta:
        ordering = ["order", "id"]


class PracticeSession(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="sessions")
    composition = models.ForeignKey(Composition, on_delete=models.CASCADE, related_name="sessions")
    minutes = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(Decimal("0.01")), MaxValueValidator(240)])
    duration_seconds = models.PositiveIntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(14400)])
    bpm = models.PositiveSmallIntegerField(null=True, blank=True, validators=[MinValueValidator(20), MaxValueValidator(240)])
    comfort = models.PositiveSmallIntegerField(default=3, validators=[MinValueValidator(1), MaxValueValidator(5)])
    notes = models.TextField(blank=True, max_length=2000)
    input_mode = models.CharField(max_length=20, default="manual", editable=False)
    created_at = models.DateTimeField(auto_now_add=True)


class LearningLesson(models.Model):
    """Versioned, authored preparation attached to one exact arrangement."""
    arrangement = models.ForeignKey(Arrangement, on_delete=models.CASCADE, related_name="lessons")
    code = models.CharField(max_length=80)
    title = models.CharField(max_length=180)
    skill = models.CharField(max_length=40)
    order = models.PositiveSmallIntegerField()
    minutes = models.PositiveSmallIntegerField(default=6)
    summary = models.TextField()
    context = models.TextField()
    content = models.JSONField(default=dict)
    quiz = models.JSONField(default=dict)
    success_criterion = models.TextField()
    content_version = models.PositiveSmallIntegerField(default=1)
    kind = models.CharField(max_length=20, default="preparation")
    # Immutable scores app primary key; integer avoids a migration cycle.
    # Historical lessons remain even if an imported file is removed.
    score_version_id = models.PositiveBigIntegerField(null=True, blank=True, editable=False)

    class Meta:
        ordering = ["order", "id"]
        constraints = [models.UniqueConstraint(fields=["arrangement", "code"], name="unique_arrangement_lesson")]


class DiagnosticAttempt(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="diagnostics")
    arrangement = models.ForeignKey(Arrangement, on_delete=models.CASCADE, related_name="diagnostics")
    answers = models.JSONField(default=dict)
    skill_scores = models.JSONField(default=dict)
    feedback = models.JSONField(default=list)
    diagnostic_version = models.PositiveSmallIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)


class LessonProgress(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="lesson_progress")
    lesson = models.ForeignKey(LearningLesson, on_delete=models.CASCADE, related_name="progress_records")
    quiz_score = models.PositiveSmallIntegerField(null=True, blank=True)
    last_quiz_at = models.DateTimeField(null=True, blank=True)
    successful_repetitions = models.PositiveSmallIntegerField(default=0)
    comfort = models.PositiveSmallIntegerField(null=True, blank=True)
    bpm = models.PositiveSmallIntegerField(null=True, blank=True)
    reflection = models.TextField(blank=True, max_length=2000)
    last_practice_at = models.DateTimeField(null=True, blank=True)
    review_due_at = models.DateTimeField(null=True, blank=True)
    review_quiz_passed_at = models.DateTimeField(null=True, blank=True)
    review_count = models.PositiveSmallIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["profile", "lesson"], name="unique_learner_lesson_progress")]


class QuizAttempt(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="quiz_attempts")
    lesson = models.ForeignKey(LearningLesson, on_delete=models.CASCADE, related_name="quiz_attempts")
    answers = models.JSONField(default=dict)
    score = models.PositiveSmallIntegerField()
    feedback = models.JSONField(default=list)
    content_version = models.PositiveSmallIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)


class LessonPracticeAttempt(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="lesson_practice_attempts")
    lesson = models.ForeignKey(LearningLesson, on_delete=models.CASCADE, related_name="practice_attempts")
    successful_repetitions = models.PositiveSmallIntegerField()
    comfort = models.PositiveSmallIntegerField()
    bpm = models.PositiveSmallIntegerField(null=True, blank=True)
    reflection = models.TextField(blank=True, max_length=2000)
    evidence = models.CharField(max_length=24, default="self_reported", editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
