from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("employee", "0001_initial"),
        ("leave", "0005_leavetype_recurring_carry_forward"),
    ]

    operations = [
        migrations.CreateModel(
            name="LeavePlan",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, null=True)),
                ("modified_at", models.DateTimeField(auto_now=True, null=True)),
                ("start_date", models.DateField(verbose_name="Start Date")),
                ("end_date", models.DateField(verbose_name="End Date")),
                ("note", models.TextField(blank=True, null=True, verbose_name="Note")),
                ("status", models.CharField(
                    choices=[("pending", "Pending"), ("approved", "Approved"), ("rejected", "Rejected")],
                    default="pending",
                    max_length=20,
                    verbose_name="Status",
                )),
                ("reject_reason", models.TextField(blank=True, null=True, verbose_name="Reject Reason")),
                ("employee_id", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="leave_plans",
                    to="employee.employee",
                    verbose_name="Employee",
                )),
                ("leave_type_id", models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    to="leave.leavetype",
                    verbose_name="Leave Type",
                )),
                ("approved_by", models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name="approved_leave_plans",
                    to="employee.employee",
                    verbose_name="Approved/Rejected By",
                )),
            ],
            options={
                "verbose_name": "Leave Plan",
                "verbose_name_plural": "Leave Plans",
                "ordering": ["-id"],
            },
        ),
    ]
