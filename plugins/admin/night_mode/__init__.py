""" Night Mode for groups """
import os

from apscheduler.jobstores.mongodb import MongoDBJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pymongo import MongoClient

from userge import config

TZ = os.environ.get("TIME_ZONE", "UTC")

monclient = MongoClient(config.DB_URI)
jobstores = {
    'default': MongoDBJobStore(
        client=monclient,
        database="Userge",
        collection='APSCHEDULER')}

# you can also import this scheduler to other plugins and use.

scheduler = AsyncIOScheduler(
    jobstores=jobstores,
    timezone=TZ)
