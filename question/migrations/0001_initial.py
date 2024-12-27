# Generated by Django 4.1.10 on 2024-12-27 05:53

from django.conf import settings
import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('map', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('question_type', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(choices=[('text', '텍스트'), ('file', '파일')], max_length=20), size=None)),
                ('description', models.TextField()),
                ('answer_validation_type', models.CharField(choices=[('text_exact', '텍스트 정확일치'), ('text_contains', '텍스트 포함'), ('regex', '정규식'), ('manual', '관리자 수동 평가')], help_text='정답 검증 방식', max_length=20)),
                ('is_by_pass', models.BooleanField(default=False, help_text='정답 검증을 하지 않음')),
                ('default_success_feedback', models.TextField(blank=True, help_text='정답 시 표시할 피드백 메시지', null=True)),
                ('default_failure_feedback', models.TextField(blank=True, help_text='오답 시 표시할 피드백 메시지', null=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('map', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='questions', to='map.map')),
            ],
            options={
                'verbose_name': '문제',
                'verbose_name_plural': '문제',
            },
        ),
        migrations.CreateModel(
            name='UserQuestionAnswer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer', models.TextField()),
                ('is_correct', models.BooleanField(blank=True, null=True)),
                ('feedback', models.TextField(blank=True, help_text='관리자의 피드백 내용', null=True)),
                ('reviewed_at', models.DateTimeField(blank=True, help_text='검토 시각', null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('map', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='user_answers', to='map.map')),
                ('member', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='question_answers', to=settings.AUTH_USER_MODEL)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='user_answers', to='question.question')),
                ('reviewed_by', models.ForeignKey(blank=True, help_text='검토한 관리자', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='reviewed_answers', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': '사용자 답변',
                'verbose_name_plural': '사용자 답변',
            },
        ),
        migrations.CreateModel(
            name='UserQuestionAnswerFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.CharField(help_text='S3 file path', max_length=255)),
                ('is_deleted', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('map', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='user_answer_files', to='map.map')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='user_answer_files', to='question.question')),
                ('user_question_answer', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='files', to='question.userquestionanswer')),
            ],
            options={
                'verbose_name': '사용자 답변 파일',
                'verbose_name_plural': '사용자 답변 파일',
            },
        ),
        migrations.CreateModel(
            name='QuestionFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.CharField(help_text='S3 file path', max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('map', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='question_files', to='map.map')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='files', to='question.question')),
            ],
            options={
                'verbose_name': '문제 파일',
                'verbose_name_plural': '문제 파일',
            },
        ),
        migrations.CreateModel(
            name='QuestionAnswer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer', models.TextField(help_text='정답')),
                ('description', models.TextField(help_text='정답에 대한 설명')),
                ('is_deleted', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('map', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='question_answers', to='map.map')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='answers', to='question.question')),
            ],
            options={
                'verbose_name': '문제 정답',
                'verbose_name_plural': '문제 정답',
            },
        ),
    ]
