from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from django.utils import timezone
from .models import Survey

# BackgroundScheduler 생성
scheduler = BackgroundScheduler()

def update_survey_status():
    current_time = timezone.now()
    surveys_to_update = Survey.objects.filter(enddated_at__lte=current_time, is_done=False)
    
    for survey in surveys_to_update:
        survey.is_done = True
        survey.save(update_fields=['is_done'])

# 분 단위로 작업 실행 (timezone.now()의 분 변경마다)
scheduler.add_job(update_survey_status, CronTrigger(minute='*'))

# 스케줄러 시작
scheduler.start()