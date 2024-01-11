import socket
import warnings
from typing import Optional

from apscheduler.events import EVENT_ALL  # noqa
from apscheduler.jobstores.base import JobLookupError
from apscheduler.schedulers.background import BackgroundScheduler

from zero import Zero
from zero.pkg.scheduler import scheduler_pb2, scheduler_pb2_grpc
from zero.pkg.scheduler.utils import fix_job_def, pop_trigger
from zero.serve.app import current


class Apscheduler:

    def __init__(self, app: Optional[Zero] = None, scheduler=None):
        self._scheduler = scheduler or BackgroundScheduler()
        self._host_name = socket.gethostname().lower()
        self._authentication_callback = None
        self.app: Optional[Zero] = None
        self.api_enabled = False
        self.allowed_hosts = ['*']

        if app:
            self.init_app(app)

    @property
    def host_name(self):
        """
        Get the host name.
        """
        return self._host_name

    @property
    def running(self):
        """
        Get true whether the scheduler is running.
        """
        return self._scheduler.running

    @property
    def state(self):
        """
        Get the state of the scheduler.
        """
        return self._scheduler.state

    @property
    def scheduler(self):
        """
        Get the base scheduler.
        """
        return self._scheduler

    @property
    def task(self):
        """
        Get the base scheduler decorator
        """
        return self._scheduler.scheduled_job

    def init_app(self, app: Zero):
        self.app = app
        current.apscheduler = self
        self._load_config()
        self._load_jobs()

        if self.api_enabled:
            self._load_api()

    def _load_api(self):
        """
        Add grpc service for apscheduler
        """
        self.app.add_service(scheduler_pb2, scheduler_pb2_grpc)
        self.app.register_view('zero.pkg.scheduler.api:SchedulerServicer', 'Scheduler')

    def start(self, paused=False):

        if self.host_name not in self.allowed_hosts and '*' not in self.allowed_hosts:
            self.app.log.debug(
                'Host name %s is not allowed to start the APScheduler. Servers allowed: %s' %
                (self.host_name, ','.join(self.allowed_hosts))
            )
            return

        self._scheduler.start(paused=paused)
        if self.app.debug:
            self.app.log.info('* The apscheduler is started')

    def shutdown(self, wait=True):
        """
        Shut down the scheduler. Does not interrupt any currently running jobs.

        :param bool wait: ``True`` to wait until all currently executing jobs have finished
        :raises SchedulerNotRunningError: if the scheduler has not been started yet
        """

        self._scheduler.shutdown(wait)

    def pause(self):
        """
        Pause job processing in the scheduler.

        This will prevent the scheduler from waking up to do job processing until :meth:`resume`
        is called. It will not however stop any already running job processing.
        """
        self._scheduler.pause()

    def resume(self):
        """
        Resume job processing in the scheduler.
        """
        self._scheduler.resume()

    def add_listener(self, callback, mask=EVENT_ALL):
        """
        Add a listener for scheduler events.

        When a matching event  occurs, ``callback`` is executed with the event object as its
        sole argument. If the ``mask`` parameter is not provided, the callback will receive events
        of all types.

        For further info: https://apscheduler.readthedocs.io/en/latest/userguide.html#scheduler-events

        :param callback: any callable that takes one argument
        :param int mask: bitmask that indicates which events should be listened to
        """
        self._scheduler.add_listener(callback, mask)

    def remove_listener(self, callback):
        """
        Remove a previously added event listener.
        """
        self._scheduler.remove_listener(callback)

    def add_job(self, id, func, **kwargs):  # noqa
        """
        Add the given job to the job list and wakes up the scheduler if it's already running.

        :param str id: explicit identifier for the job (for modifying it later)
        :param func: callable (or a textual reference to one) to run at the given time
        """

        job_def = dict(kwargs)
        job_def['id'] = id
        job_def['func'] = func
        job_def['name'] = job_def.get('name') or id

        fix_job_def(job_def)

        return self._scheduler.add_job(**job_def)

    def delete_all_jobs(self, jobstore=None):
        """
        DEPRECATED, use remove_all_jobs instead.

        Remove all jobs from the specified job store, or all job stores if none is given.

        :param str|unicode jobstore: alias of the job store
        """

        warnings.warn('delete_all_jobs has been deprecated, use remove_all_jobs instead.', DeprecationWarning)

        self.remove_all_jobs(jobstore)

    def remove_job(self, id, jobstore=None):  # noqa
        """
        Delete the job and prevent it from continuing to run.

        :param str id: the identifier of the job
        :param str jobstore: alias of the job store that contains the job
        """

        self._scheduler.remove_job(id, jobstore)  # noqa

    def remove_all_jobs(self, jobstore=None):
        """
        Remove all jobs from the specified job store, or all job stores if none is given.

        :param str|unicode jobstore: alias of the job store
        """

        self._scheduler.remove_all_jobs(jobstore)

    def get_job(self, id, jobstore=None):  # noqa
        """
        Return the Job that matches the given ``id``.
        """

        return self._scheduler.get_job(id, jobstore)  # noqa   # noqa

    def get_jobs(self, jobstore=None):
        """
        Return a list of pending jobs (if the scheduler hasn't been started yet) and scheduled jobs, either from a
        specific job store or from all of them.

        :param str jobstore: alias of the job store
        :rtype: list[Job]
        """

        return self._scheduler.get_jobs(jobstore)

    def modify_job(self, id, jobstore=None, **changes):  # noqa
        """
        Modify the properties of a single job. Modifications are passed to this method as extra keyword arguments.

        :param str id: the identifier of the job
        :param str jobstore: alias of the job store that contains the job
        """

        fix_job_def(changes)

        if 'trigger' in changes:
            trigger, trigger_args = pop_trigger(changes)
            self._scheduler.reschedule_job(id, jobstore, trigger, **trigger_args)

        return self._scheduler.modify_job(id, jobstore, **changes)

    def pause_job(self, id, jobstore=None):  # noqa
        """
        Pause the given job until it is explicitly resumed.

        :param str id: the identifier of the job
        :param str jobstore: alias of the job store that contains the job
        """
        self._scheduler.pause_job(id, jobstore)  # noqa

    def resume_job(self, id, jobstore=None):  # noqa
        """
        Resume the schedule of the given job, or removes the job if its schedule is finished.

        :param str id: the identifier of the job
        :param str jobstore: alias of the job store that contains the job
        """
        self._scheduler.resume_job(id, jobstore)  # noqa

    def run_job(self, id, jobstore=None):  # noqa
        """
        Run the given job without scheduling it.
        :param id: the identifier of the job.
        :param str jobstore: alias of the job store that contains the job
        :return:
        """
        job = self._scheduler.get_job(id, jobstore)

        if not job:
            raise JobLookupError(id)

        job.func(*job.args, **job.kwargs)

    def _load_config(self):
        """
        Load the configuration from the Zero configuration.
        """
        options = dict()

        job_stores = getattr(self.app.setting, 'SCHEDULER_JOBSTORES', None)
        if job_stores:
            options['jobstores'] = job_stores

        executors = getattr(self.app.setting, 'SCHEDULER_EXECUTORS', None)
        if executors:
            options['executors'] = executors

        job_defaults = getattr(self.app.setting, 'SCHEDULER_JOB_DEFAULTS', None)
        if job_defaults:
            options['job_defaults'] = job_defaults

        timezone = getattr(self.app.setting, 'SCHEDULER_TIMEZONE', None)
        if timezone:
            options['timezone'] = timezone

        self._scheduler.configure(**options)

        self.allowed_hosts = getattr(self.app.setting, 'SCHEDULER_ALLOWED_HOSTS', self.allowed_hosts)
        self.api_enabled = getattr(self.app.setting, 'SCHEDULER_API_ENABLED', self.api_enabled)

    def _load_jobs(self):
        """
        Load the job definitions from the Zero configuration.
        """
        jobs = getattr(self.app.setting, 'SCHEDULER_JOBS', None)

        if not jobs:
            jobs = getattr(self.app.setting, 'JOBS', None)

        if jobs:
            for job in jobs:
                self.add_job(**job)
