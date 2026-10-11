from django.contrib import admin
from .models import Arrangement, Composition, DiagnosticAttempt, LearningLesson, LessonPracticeAttempt, LessonProgress, PracticePlan, PracticeSession, PracticeTask, Profile, QuizAttempt

admin.site.register([Profile, Composition, Arrangement, PracticePlan, PracticeTask, PracticeSession])
admin.site.register([DiagnosticAttempt, LearningLesson, LessonPracticeAttempt, LessonProgress, QuizAttempt])
