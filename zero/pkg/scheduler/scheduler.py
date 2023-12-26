import socket
import warnings
from typing import Optional

from apscheduler.events import EVENT_ALL  # noqa
from apscheduler.jobstores.base import JobLookupError
from apscheduler.schedulers.background import BackgroundScheduler

from zero import Zero
from zero.pkg.base import ZeroPkgInitBase
from zero.pkg.scheduler.utils import fix_job_def, pop_trigger


class Apscheduler(ZeroPkgInitBase):

    def __init__(self, app: Optional[Zero] = None, scheduler=None):
        self._scheduler = scheduler or BackgroundScheduler()
        self._host_name = socket.gethostname().lower()
        self._authentication_callback = None
        self.app: Optional[Zero] = None

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
        self.app.apscheduler = self
        self._load_config()
        self._load_jobs()

    def start(self, paused=False):
        self._scheduler.start(paused=paused)

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

    def add_job(self, jid, func, **kwargs):
        """
        Add the given job to the job list and wakes up the scheduler if it's already running.

        :param str jid: explicit identifier for the job (for modifying it later)
        :param func: callable (or a textual reference to one) to run at the given time
        """

        job_def = dict(kwargs)
        job_def['id'] = jid
        job_def['func'] = func
        job_def['name'] = job_def.get('name') or jid

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

    def remove_job(self, jid, jobstore=None):
        """
        Delete the job and prevent it from continuing to run.

        :param str jid: the identifier of the job
        :param str jobstore: alias of the job store that contains the job
        """

        self._scheduler.remove_job(jid, jobstore)

    def remove_all_jobs(self, jobstore=None):
        """
        Remove all jobs from the specified job store, or all job stores if none is given.

        :param str|unicode jobstore: alias of the job store
        """

        self._scheduler.remove_all_jobs(jobstore)

    def get_job(self, jid, jobstore=None):
        """
        Return the Job that matches the given ``id``.
        """

        return self._scheduler.get_job(jid, jobstore)

    def get_jobs(self, jobstore=None):
        """
        Return a list of pending jobs (if the scheduler hasn't been started yet) and scheduled jobs, either from a
        specific job store or from all of them.

        :param str jobstore: alias of the job store
        :rtype: list[Job]
        """

        return self._scheduler.get_jobs(jobstore)

    def modify_job(self, jid, jobstore=None, **changes):
        """
        Modify the properties of a single job. Modifications are passed to this method as extra keyword arguments.

        :param str jid: the identifier of the job
        :param str jobstore: alias of the job store that contains the job
        """

        fix_job_def(changes)

        if 'trigger' in changes:
            trigger, trigger_args = pop_trigger(changes)
            self._scheduler.reschedule_job(jid, jobstore, trigger, **trigger_args)

        return self._scheduler.modify_job(jid, jobstore, **changes)

    def pause_job(self, jid, jobstore=None):
        """
        Pause the given job until it is explicitly resumed.

        :param str jid: the identifier of the job
        :param str jobstore: alias of the job store that contains the job
        """
        self._scheduler.pause_job(jid, jobstore)

    def resume_job(self, jid, jobstore=None):
        """
        Resume the schedule of the given job, or removes the job if its schedule is finished.

        :param str jid: the identifier of the job
        :param str jobstore: alias of the job store that contains the job
        """
        self._scheduler.resume_job(jid, jobstore)

    def run_job(self, jid, jobstore=None):
        """
        Run the given job without scheduling it.
        :param jid: the identifier of the job.
        :param str jobstore: alias of the job store that contains the job
        :return:
        """
        job = self._scheduler.get_job(jid, jobstore)

        if not job:
            raise JobLookupError(id)

        job.func(*job.args, **job.kwargs)

    def _load_config(self):
        """
        Load the configuration from the Zero configuration.
        """
        options = dict()

        job_stores = getattr(self.app.setting, 'SCHEDULER_JOBSTORES')
        if job_stores:
            options['jobstores'] = job_stores

        executors = getattr(self.app.setting, 'SCHEDULER_EXECUTORS')
        if executors:
            options['executors'] = executors

        job_defaults = getattr(self.app.setting, 'SCHEDULER_JOB_DEFAULTS')
        if job_defaults:
            options['job_defaults'] = job_defaults

        timezone = getattr(self.app.setting, 'SCHEDULER_TIMEZONE')
        if timezone:
            options['timezone'] = timezone

        self._scheduler.configure(**options)

    def _load_jobs(self):
        """
        Load the job definitions from the Zero configuration.
        """
        jobs = getattr(self.app.setting, 'SCHEDULER_JOBS')

        if not jobs:
            jobs = getattr(self.app.setting, 'JOBS')

        if jobs:
            for job in jobs:
                self.add_job(**job)
