from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("reports", "0003_arus_kas_template"),
    ]

    operations = [
        migrations.AddField(
            model_name="templateitem",
            name="level",
            field=models.PositiveIntegerField(default=0),
        ),
    ]
