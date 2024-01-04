import json
from datetime import datetime

import grpc  # noqa
from apscheduler.jobstores.base import ConflictingIdError, JobLookupError

from zero.pkg.scheduler.utils import job_to_dict
from zero.serve.app import current, resp


class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super(JSONEncoder, self).default(obj)


class SchedulerServicer:

    @resp('GetSchInfoResp')
    def get_scheduler_info(self, request, context, response):  # noqa
        """
        Gets the scheduler info.
        """
        scheduler = current.apscheduler  # noqa
        return response(
            current_host=scheduler.host_name,
            allowed_hosts=scheduler.allowed_hosts,
            running=scheduler.running)

    @resp('JobInfoResp')
    def add_job(self, request, context, response):
        """
        Adds a new job.
        """
        try:
            data: dict = json.loads(request.json)
            try:
                if not isinstance(data, dict):
                    context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                    context.set_details('The request parameter format is incorrect.')
                    return response()
                job = current.apscheduler.add_job(**data)  # noqa
                return response(job=json.dumps(job_to_dict(job), cls=JSONEncoder))
            except ConflictingIdError:
                context.set_code(grpc.StatusCode.ALREADY_EXISTS)
                context.set_details('Job %s already exists.' % data.get('id'))
                return response()
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return response()

    @resp('JobInfoResp')
    def get_job(self, request, context, response):
        """
        Gets a job.
        """
        job_id = request.id
        job = current.apscheduler.get_job(job_id)

        if not job:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f'Job {job_id} not found.')
            return response()

        return response(job=json.dumps(job_to_dict(job), cls=JSONEncoder))

    @resp('JobInfosResp')
    def get_jobs(self, request, context, response):
        """
        Gets all scheduled jobs.
        """
        jobs = current.apscheduler.get_jobs()
        job_states = []
        for job in jobs:
            job_states.append(job_to_dict(job))
        return response(jobs=json.dumps(jobs, cls=JSONEncoder))

    @resp('EmptyResp')
    def delete_job(self, request, context, response):
        """
        Deletes a job.
        """
        job_id = request.id

        try:
            current.apscheduler.remove_job(job_id)  # noqa
            return response()
        except JobLookupError:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f'Job {job_id} not found.')
            return response()
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return response()

    @resp('JobInfoResp')
    def update_job(self, request, context, response):
        """
        Updates a job.
        """
        try:
            job_id: str = request.id
            data: dict = json.loads(request.json)
            try:
                if not isinstance(data, dict):
                    context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                    context.set_details('The request parameter format is incorrect.')
                    return response()
                current.apscheduler.modify_job(job_id, **data)
                job = current.apscheduler.get_job(job_id)
                return response(job=json.dumps(job_to_dict(job), cls=JSONEncoder))
            except JobLookupError:
                context.set_code(grpc.StatusCode.ALREADY_EXISTS)
                context.set_details(f'Job {job_id} not found.')
                return response()
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return response()

    @resp('JobInfoResp')
    def pause_job(self, request, context, response):
        """
        Pauses a job.
        """
        job_id: str = request.id
        try:
            current.apscheduler.pause_job(job_id)
            job = current.apscheduler.get_job(job_id)
            return response(job=json.dumps(job_to_dict(job), cls=JSONEncoder))
        except JobLookupError:
            context.set_code(grpc.StatusCode.ALREADY_EXISTS)
            context.set_details(f'Job {job_id} not found.')
            return response()
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return response()

    @resp('JobInfoResp')
    def resume_job(self, request, context, response):
        """
        Resumes a job.
        """
        job_id: str = request.id
        try:
            current.apscheduler.resume_job(job_id)
            job = current.apscheduler.get_job(job_id)
            return response(job=json.dumps(job_to_dict(job), cls=JSONEncoder))
        except JobLookupError:
            context.set_code(grpc.StatusCode.ALREADY_EXISTS)
            context.set_details(f'Job {job_id} not found.')
            return response()
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return response()

    @resp('JobInfoResp')
    def run_job(self, request, context, response):
        """
        Executes a job.
        """
        job_id: str = request.id
        try:
            current.apscheduler.run_job(job_id)
            job = current.apscheduler.get_job(job_id)
            return response(job=json.dumps(job_to_dict(job), cls=JSONEncoder))
        except JobLookupError:
            context.set_code(grpc.StatusCode.ALREADY_EXISTS)
            context.set_details(f'Job {job_id} not found.')
            return response()
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return response()
