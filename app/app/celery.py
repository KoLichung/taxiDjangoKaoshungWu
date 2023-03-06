import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
app = Celery('app')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # sender.add_periodic_task(60.0, test_add.s('world'), expires=10)
    # sender.add_periodic_task(30.0, test_get_user_count.s('world'), expires=10)
    sender.add_periodic_task(2.0, case_ship_count_down.s('world'), expires=10)

    #run at 0800 of first day of month every taiwan time
    # sender.add_periodic_task(
    #     crontab(hour=1, minute=0, day_of_month='1'),
    #     cal_month_summary.s('calcualte month summary'),
    # )

@app.task
def case_ship_count_down(arg):
    from task.tasks import countDownUserCaseShip
    countDownUserCaseShip()

# @app.task
# def cal_month_summary(arg):
#     from task.tasks import createMonthSummary
#     createMonthSummary()

@app.task
def test_add(arg):
    from task.tasks import add
    add(5,6)

@app.task
def test_get_user_count(arg):
    from task.tasks import getUserCount
    getUserCount()