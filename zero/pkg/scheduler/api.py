import grpc  # noqa
from apscheduler.jobstores.base import ConflictingIdError, JobLookupError

from zero import View
from zero.serve.app import current


class SchedulerServicer(View):

    def get_scheduler_info(self, request, context):  # noqa
        from zero.pkg.scheduler.scheduler import Apscheduler
        scheduler: Apscheduler = current._apscheduler  # noqa
        return self.pb2.GetSchInfoResp(
            current_host=scheduler.host_name,
            allowed_hosts=scheduler.allowed_hosts,
            running=scheduler.running)

    def add_job(self, request, context):
        data = {'id': request.id, 'func': request.func, 'trigger': request.trigger}

        try:
            current._apscheduler.add_job(**data)  # noqa
            return self.pb2.AddJobResp()
        except ConflictingIdError:
            context.set_code(grpc.StatusCode.ALREADY_EXISTS)
            context.set_details('Job %s already exists.' % data.get('id'))
            return self.pb2.AddJobResp()
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return self.pb2.AddJobResp()

    def get_job(self, request, context):
        pass

    def get_jobs(self, request, context):
        pass

    def delete_job(self, request, context):
        job_id = request.id

        try:
            current._apscheduler.remove_job(job_id)  # noqa
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
        pass

    def pause_job(self, request, context):
        pass

    def resume_job(self, request, context):
        pass

    def run_job(self, request, context):
        pass
