from apscheduler.schedulers.blocking import BlockingScheduler
import subprocess

scheduler = BlockingScheduler()

@scheduler.scheduled_job('cron', hour='*/6')
def scheduled_data_ingestion():
    subprocess.call(['python', 'data_ingestion.py'])

@scheduler.scheduled_job('cron', hour='*/12')
def scheduled_content_processing():
    subprocess.call(['python', 'content_processing.py'])

if __name__ == "__main__":
    scheduler.start()
,m,