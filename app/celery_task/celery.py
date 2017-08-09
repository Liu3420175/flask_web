from celery import Celery


celery = Celery('celery_task', include=['celery_task.tasks'])

celery.config_from_object('celery_task.celeryconfig')


if __name__ == '__main__':

    celery.start()