from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("leave", "0002_add_conditional_formatting_and_gender_restriction"),
    ]

    operations = [
        migrations.AddField(
            model_name="leavetype",
            name="monthly_recurring",
            field=models.BooleanField(
                default=False,
                help_text="If enabled, employees assigned this leave type will receive the allocated leave days every month automatically.",
                verbose_name="Monthly Recurring",
            ),
        ),
    ]
