import os
import traceback
import logging
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from sesame_automate.models.enums.state import State
from sesame_automate.runnables import *

def setup_logging():
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    logs_dir = 'logs'
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.FileHandler(f'{logs_dir}/sesame_automate.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger('SesameAutomate')

logger = setup_logging()

try:
    from dotenv import load_dotenv
    load_dotenv()
    logger.info("Environment variables loaded from .env file")
except ImportError:
    logger.warning("python-dotenv not installed. Make sure to set environment variables manually.")

current_state: State = State.UNKNOWN

def main():
    login = SesameTimeLoginRunnable()
    me = SesameTimeMeInfoRunnable()
    work_break = SesameTimeWorkBreakRunnable()
    assigned_work_check_types = SesameTimeAssignedWorkCheckTypesRunnable()
    check_in = SesameTimeCheckInRunnable()
    check_out = SesameTimeCheckOutRunnable()

    logger.info("Welcome, Sesame Time Automate is starting...")
    runnable = login | me | work_break | assigned_work_check_types
    runnable.invoke({
        "is_welcome": True
    })

    logger.info("Background jobs starting...")

    scheduler = BlockingScheduler(timezone=os.getenv("TIME_ZONE"))
    if not os.getenv("IN_TIME_CRON"):
        logger.warning("IN_TIME_CRON not set. Please set it in the environment variables to schedule check in jobs.")
        exit(1)

    if not os.getenv("OUT_TIME_CRON"):
        logger.warning("OUT_TIME_CRON not set. Please set it in the environment variables to schedule check out jobs.")
        exit(1)

    if not os.getenv("BREAK_START_CRON"):
        logger.warning("BREAK_START_CRON not set. Please set it in the environment variables to schedule break start jobs.")
        exit(1)

    if not os.getenv("BREAK_END_CRON"):
        logger.warning("BREAK_END_CRON not set. Please set it in the environment variables to schedule break end jobs.")
        exit(1)
    
    def in_time_job():
        try:
            logger.info("Executing Check In Job")
            current_state = State.WORKING
            runnable = login | me | assigned_work_check_types | check_in
            runnable.invoke({
                "current_state": current_state,
            })
            logger.info("Check In Job Executed")
        except Exception as e:
            logger.error(f"Error during Check In Job: {e}")
            traceback.print_exc()
    
    def out_time_job():
        try:
            logger.info("Executing Check Out Job")
            current_state = State.WORKING
            runnable = login | me | assigned_work_check_types | check_out
            runnable.invoke({
                "current_state": current_state,
            })
            logger.info("Check Out Job Executed")
        except Exception as e:
            logger.error(f"Error during Check Out Job: {e}")
            traceback.print_exc()

    def break_start_job():
        try:
            logger.info("Executing Break Start Job")
            current_state = State.WORKING
            base_runnable = login | me | assigned_work_check_types | work_break
            runnable = base_runnable | check_out
            runnable.invoke({
                "current_state": current_state,
            })
            current_state = State.BREAK
            runnable = base_runnable | check_in
            runnable.invoke({
                "current_state": current_state,
            })
            logger.info("Break Start Job Executed")
        except Exception as e:
            logger.error(f"Error during Break Start Job: {e}")
            traceback.print_exc()

    def break_finished_job():
        try:
            logger.info("Executing Break Finished Job")
            current_state = State.BREAK
            base_runnable = login | me | assigned_work_check_types | work_break
            runnable = base_runnable | check_out
            runnable.invoke({
                "current_state": current_state,
            })
            current_state = State.WORKING
            runnable = base_runnable | check_in
            runnable.invoke({
                "current_state": current_state,
            })
            logger.info("Break Finished Job Executed")
        except Exception as e:
            logger.error(f"Error during Break Finished Job: {e}")
            traceback.print_exc()

    for cron in os.getenv("IN_TIME_CRON", "").split(','):
        scheduler.add_job(
            func=in_time_job,
            trigger=CronTrigger.from_crontab(cron),
            name='Check In Job'
        )
    
    for cron in os.getenv("OUT_TIME_CRON", "").split(','):
        scheduler.add_job(
            func=out_time_job,
            trigger=CronTrigger.from_crontab(cron),
            name='Check Out Job'
        )

    scheduler.add_job(
        func=break_start_job,
        trigger=CronTrigger.from_crontab(os.getenv("BREAK_START_CRON")),
        name='Break Start Job'
    )

    scheduler.add_job(
        func=break_finished_job,
        trigger=CronTrigger.from_crontab(os.getenv("BREAK_END_CRON")),
        name='Break End Job'
    )

    logger.info("Waiting for scheduled jobs to run...")
    
    scheduler.start()