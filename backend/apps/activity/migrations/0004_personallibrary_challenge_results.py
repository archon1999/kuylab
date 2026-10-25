from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("activity", "0003_personallibrary_comfortable_speeds_practicenote")]

    operations = [
        migrations.AddField(
            model_name="personallibrary", name="challenge_results",
            field=models.JSONField(default=dict),
        ),
    ]
