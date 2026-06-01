from django.db import migrations


def update_payment_codes(apps, schema_editor):
    Application = apps.get_model('portal', 'Application')
    mapping = {
        'card': 'mir',
        'invoice': 'qr',
        'cash': 'office',
    }
    for old, new in mapping.items():
        Application.objects.filter(payment_method=old).update(payment_method=new)


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(update_payment_codes, migrations.RunPython.noop),
    ]
