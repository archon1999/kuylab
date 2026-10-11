from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [("scores", "0002_score_completeness_verified_at_score_file_format_and_more")]
    operations = [migrations.CreateModel(name="StudioAsset", fields=[
        ("key", models.CharField(max_length=100, primary_key=True, serialize=False)),
        ("revision", models.CharField(max_length=40)),
        ("score", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="studio_asset", to="scores.score")),
    ])]
