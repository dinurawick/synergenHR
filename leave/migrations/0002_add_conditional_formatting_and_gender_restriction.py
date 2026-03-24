# Generated manually

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('leave', '0001_initial'),
        ('payroll', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='leavetype',
            name='use_conditional_formatting',
            field=models.BooleanField(
                default=False,
                help_text='Apply Python-based rules for leave allocation (e.g., based on employee type)',
                verbose_name='Use Conditional Formatting'
            ),
        ),
        migrations.AddField(
            model_name='leavetype',
            name='conditional_formatting_rule',
            field=models.ForeignKey(
                blank=True,
                help_text='Select a conditional formatting rule to apply',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='leave_types',
                to='payroll.conditionalformatting',
                verbose_name='Conditional Formatting Rule'
            ),
        ),
        migrations.AddField(
            model_name='leavetype',
            name='gender_restriction',
            field=models.CharField(
                choices=[
                    ('all', 'All Genders'),
                    ('male', 'Male Only'),
                    ('female', 'Female Only'),
                    ('other', 'Other Only')
                ],
                default='all',
                help_text='Restrict this leave type to specific gender (e.g., maternity leave for females only)',
                max_length=10,
                verbose_name='Gender Restriction'
            ),
        ),
    ]
