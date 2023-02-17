# Generated by Django 4.1.7 on 2023-02-17 20:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('communication', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='communicationhistory',
            name='template_type',
            field=models.CharField(choices=[('accounts_password_reset', 'Восстановление пароля'), ('accounts_password_reset_otp', 'Восстановление пароля одноразовым кодом'), ('accounts_password_reset_magic_link', 'Восстановление пароля через magic link'), ('accounts_email_confirm', 'Подтверждение адреса эл. почты')], db_index=True, max_length=50),
        ),
        migrations.AlterField(
            model_name='historicaltemplate',
            name='type',
            field=models.CharField(choices=[('accounts_password_reset', 'Восстановление пароля'), ('accounts_password_reset_otp', 'Восстановление пароля одноразовым кодом'), ('accounts_password_reset_magic_link', 'Восстановление пароля через magic link'), ('accounts_email_confirm', 'Подтверждение адреса эл. почты')], max_length=50),
        ),
        migrations.AlterField(
            model_name='template',
            name='type',
            field=models.CharField(choices=[('accounts_password_reset', 'Восстановление пароля'), ('accounts_password_reset_otp', 'Восстановление пароля одноразовым кодом'), ('accounts_password_reset_magic_link', 'Восстановление пароля через magic link'), ('accounts_email_confirm', 'Подтверждение адреса эл. почты')], max_length=50),
        ),
    ]
