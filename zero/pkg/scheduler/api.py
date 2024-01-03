import json
from datetime import datetime

import grpc  # noqa
from apscheduler.jobstores.base import ConflictingIdError, JobLookupError

from zero import View
from zero.pkg.scheduler.utils import job_to_dict
from zero.serve.app import current


class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super(JSONEncoder, self).default(obj)


class SchedulerServicer(View):

    def get_scheduler_info(self, request, context):  # noqa
        """
        Gets the scheduler info.
        """
        scheduler = current.apscheduler  # noqa
        resp = self.pb2.GetSchInfoResp(
            current_host=scheduler.host_name,
            allowed_hosts=scheduler.allowed_hosts,
            running=scheduler.running)
        return resp

    def add_job(self, request, context):
        """
        Adds a new job.
        """
        try:
            data: dict = json.loads(request.json)
            try:
                if not isinstance(data, dict):
                    context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                    context.set_details('The request parameter format is incorrect.')
                    return self.pb2.JobInfoResp()
                job = current.apscheduler.add_job(**data)  # noqa
                return  self.pb2.JobInfoResp(job=json.dumps(job_to_dict(job), cls=JSONEncoder))
            except ConflictingIdError:
                context.set_code(grpc.StatusCode.ALREADY_EXISTS)
                context.set_details('Job %s already exists.' % data.get('id'))
                return self.pb2.JobInfoResp()
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return self.pb2.JobInfoResp()

    def get_job(self, request, context):
        """
        Gets a job.
        """
        job_id = request.id
        job = current.apscheduler.get_job(job_id)

        if not job:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f'Job {job_id} not found.')
            return self.pb2.JobInfoResp()

        job_to_dict(job)

        return self.pb2.JobInfoResp(job=json.dumps(job, cls=JSONEncoder))

    def get_jobs(self, request, context):
        """
        Gets all scheduled jobs.
        """
        jobs = current.apscheduler.get_jobs()
        job_states = []
        for job in jobs:
            job_states.append(job_to_dict(job))
        return self.pb2.JobInfosResp(jobs=json.dumps(jobs, cls=JSONEncoder))

    def delete_job(self, request, context):
        """
        Deletes a job.
        """
        job_id = request.id

        try:
            current.apscheduler.remove_job(job_id)  # noqa
            return self.pb2.EmptyResp()
        except JobLookupError:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f'Job {job_id} not found.')
            return self.pb2.EmptyResp()
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return self.pb2.EmptyResp()

    def update_job(self, request, context):
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
                    return self.pb2.JobInfoResp()
                current.apscheduler.modify_job(job_id, **data)
                job = current.apscheduler.get_job(job_id)
                return self.pb2.JobInfoResp(job=json.dumps(job_to_dict(job), cls=JSONEncoder))
            except JobLookupError:
                context.set_code(grpc.StatusCode.ALREADY_EXISTS)
                context.set_details(f'Job {job_id} not found.')
                return self.pb2.JobInfoResp()
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return self.pb2.JobInfoResp()

    def pause_job(self, request, context):
        """
        Pauses a job.
        """
        job_id: str = request.id
        try:
            current.apscheduler.pause_job(job_id)
            job = current.apscheduler.get_job(job_id)
            return self.pb2.JobInfoResp(job=json.dumps(job_to_dict(job), cls=JSONEncoder))
        except JobLookupError:
            context.set_code(grpc.StatusCode.ALREADY_EXISTS)
            context.set_details(f'Job {job_id} not found.')
            return self.pb2.JobInfoResp()
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return self.pb2.JobInfoResp()

    def resume_job(self, request, context):
        """
        Resumes a job.
        """
        job_id: str = request.id
        try:
            current.apscheduler.resume_job(job_id)
            job = current.apscheduler.get_job(job_id)
            return self.pb2.JobInfoResp(job=json.dumps(job_to_dict(job), cls=JSONEncoder))
        except JobLookupError:
            context.set_code(grpc.StatusCode.ALREADY_EXISTS)
            context.set_details(f'Job {job_id} not found.')
            return self.pb2.JobInfoResp()
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return self.pb2.JobInfoResp()

    def run_job(self, request, context):
        """
        Executes a job.
        """
        job_id: str = request.id
        try:
            current.apscheduler.run_job(job_id)
            job = current.apscheduler.get_job(job_id)
            return self.pb2.JobInfoResp(job=json.dumps(job_to_dict(job), cls=JSONEncoder))
        except JobLookupError:
            context.set_code(grpc.StatusCode.ALREADY_EXISTS)
            context.set_details(f'Job {job_id} not found.')
            return self.pb2.JobInfoResp()
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return self.pb2.JobInfoResp()
