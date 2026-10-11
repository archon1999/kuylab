from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [("learning", "0007_alter_arrangement_options_and_more")]
    operations = [
        migrations.CreateModel(name="PersonalLibrary", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("favorites", models.JSONField(default=list)), ("recents", models.JSONField(default=list)),
            ("positions", models.JSONField(default=dict)),
            ("profile", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to="learning.profile")),
        ]),
        migrations.CreateModel(name="SiteVisit", fields=[
            ("id", models.UUIDField(editable=False, primary_key=True, serialize=False)),
            ("started_at", models.DateTimeField()), ("seconds", models.PositiveIntegerField()),
            ("content_seconds", models.JSONField(default=dict)), ("day_seconds", models.JSONField(default=dict)),
            ("updated_at", models.DateTimeField(auto_now=True)),
            ("profile", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="learning.profile")),
        ], options={"ordering": ["-started_at"]}),
    ]
