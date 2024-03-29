# Generated by Django 4.2.8 on 2024-01-03 18:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0012_alter_order_shipping_address_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='total_payed_amount',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name='payment_info',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('card_number', models.CharField(max_length=255)),
                ('expiry_date', models.CharField(max_length=5)),
                ('cvc', models.CharField(max_length=3)),
                ('card_holder_name', models.CharField(max_length=255)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order_payment_info', to='app1.order')),
            ],
        ),
    ]
