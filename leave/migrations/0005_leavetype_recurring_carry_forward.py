from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("leave", "0004_merge_20260326_0920"),
    ]

    operations = [
        migrations.AddField(
            model_name="leavetype",
            name="recurring_carry_forward",
            field=models.BooleanField(
                default=False,
                help_text="If enabled, unused leave days from the previous month carry over to the next month.",
                verbose_name="Recurring Carry Forward",
            ),
        ),
    ]
