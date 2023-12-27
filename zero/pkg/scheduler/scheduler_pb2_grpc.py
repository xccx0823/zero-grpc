# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

from zero.pkg.scheduler import scheduler_pb2 as scheduler__pb2


class SchedulerStub(object):
    """Scheduler: Apscheduler Task information
    """

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.GetSchedulerInfo = channel.unary_unary(
                '/Scheduler/GetSchedulerInfo',
                request_serializer=scheduler__pb2.EmptyRequest.SerializeToString,
                response_deserializer=scheduler__pb2.GetSchInfoResp.FromString,
                )
        self.AddJob = channel.unary_unary(
                '/Scheduler/AddJob',
                request_serializer=scheduler__pb2.AddJobRequest.SerializeToString,
                response_deserializer=scheduler__pb2.AddJobResp.FromString,
                )
        self.GetJob = channel.unary_unary(
                '/Scheduler/GetJob',
                request_serializer=scheduler__pb2.JobIdRequest.SerializeToString,
                response_deserializer=scheduler__pb2.GetJobResp.FromString,
                )
        self.GetJobs = channel.unary_unary(
                '/Scheduler/GetJobs',
                request_serializer=scheduler__pb2.EmptyRequest.SerializeToString,
                response_deserializer=scheduler__pb2.EmptyResp.FromString,
                )
        self.DeleteJob = channel.unary_unary(
                '/Scheduler/DeleteJob',
                request_serializer=scheduler__pb2.JobIdRequest.SerializeToString,
                response_deserializer=scheduler__pb2.EmptyResp.FromString,
                )
        self.UpdateJob = channel.unary_unary(
                '/Scheduler/UpdateJob',
                request_serializer=scheduler__pb2.JobIdRequest.SerializeToString,
                response_deserializer=scheduler__pb2.EmptyResp.FromString,
                )
        self.PauseJob = channel.unary_unary(
                '/Scheduler/PauseJob',
                request_serializer=scheduler__pb2.JobIdRequest.SerializeToString,
                response_deserializer=scheduler__pb2.EmptyResp.FromString,
                )
        self.ResumeJob = channel.unary_unary(
                '/Scheduler/ResumeJob',
                request_serializer=scheduler__pb2.JobIdRequest.SerializeToString,
                response_deserializer=scheduler__pb2.EmptyResp.FromString,
                )
        self.RunJob = channel.unary_unary(
                '/Scheduler/RunJob',
                request_serializer=scheduler__pb2.JobIdRequest.SerializeToString,
                response_deserializer=scheduler__pb2.EmptyResp.FromString,
                )


class SchedulerServicer(object):
    """Scheduler: Apscheduler Task information
    """

    def GetSchedulerInfo(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def AddJob(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetJob(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetJobs(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def DeleteJob(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def UpdateJob(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def PauseJob(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def ResumeJob(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def RunJob(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_SchedulerServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'GetSchedulerInfo': grpc.unary_unary_rpc_method_handler(
                    servicer.GetSchedulerInfo,
                    request_deserializer=scheduler__pb2.EmptyRequest.FromString,
                    response_serializer=scheduler__pb2.GetSchInfoResp.SerializeToString,
            ),
            'AddJob': grpc.unary_unary_rpc_method_handler(
                    servicer.AddJob,
                    request_deserializer=scheduler__pb2.AddJobRequest.FromString,
                    response_serializer=scheduler__pb2.AddJobResp.SerializeToString,
            ),
            'GetJob': grpc.unary_unary_rpc_method_handler(
                    servicer.GetJob,
                    request_deserializer=scheduler__pb2.JobIdRequest.FromString,
                    response_serializer=scheduler__pb2.GetJobResp.SerializeToString,
            ),
            'GetJobs': grpc.unary_unary_rpc_method_handler(
                    servicer.GetJobs,
                    request_deserializer=scheduler__pb2.EmptyRequest.FromString,
                    response_serializer=scheduler__pb2.EmptyResp.SerializeToString,
            ),
            'DeleteJob': grpc.unary_unary_rpc_method_handler(
                    servicer.DeleteJob,
                    request_deserializer=scheduler__pb2.JobIdRequest.FromString,
                    response_serializer=scheduler__pb2.EmptyResp.SerializeToString,
            ),
            'UpdateJob': grpc.unary_unary_rpc_method_handler(
                    servicer.UpdateJob,
                    request_deserializer=scheduler__pb2.JobIdRequest.FromString,
                    response_serializer=scheduler__pb2.EmptyResp.SerializeToString,
            ),
            'PauseJob': grpc.unary_unary_rpc_method_handler(
                    servicer.PauseJob,
                    request_deserializer=scheduler__pb2.JobIdRequest.FromString,
                    response_serializer=scheduler__pb2.EmptyResp.SerializeToString,
            ),
            'ResumeJob': grpc.unary_unary_rpc_method_handler(
                    servicer.ResumeJob,
                    request_deserializer=scheduler__pb2.JobIdRequest.FromString,
                    response_serializer=scheduler__pb2.EmptyResp.SerializeToString,
            ),
            'RunJob': grpc.unary_unary_rpc_method_handler(
                    servicer.RunJob,
                    request_deserializer=scheduler__pb2.JobIdRequest.FromString,
                    response_serializer=scheduler__pb2.EmptyResp.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'Scheduler', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class Scheduler(object):
    """Scheduler: Apscheduler Task information
    """

    @staticmethod
    def GetSchedulerInfo(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/Scheduler/GetSchedulerInfo',
            scheduler__pb2.EmptyRequest.SerializeToString,
            scheduler__pb2.GetSchInfoResp.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def AddJob(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/Scheduler/AddJob',
            scheduler__pb2.AddJobRequest.SerializeToString,
            scheduler__pb2.AddJobResp.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GetJob(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/Scheduler/GetJob',
            scheduler__pb2.JobIdRequest.SerializeToString,
            scheduler__pb2.GetJobResp.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GetJobs(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/Scheduler/GetJobs',
            scheduler__pb2.EmptyRequest.SerializeToString,
            scheduler__pb2.EmptyResp.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def DeleteJob(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/Scheduler/DeleteJob',
            scheduler__pb2.JobIdRequest.SerializeToString,
            scheduler__pb2.EmptyResp.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def UpdateJob(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/Scheduler/UpdateJob',
            scheduler__pb2.JobIdRequest.SerializeToString,
            scheduler__pb2.EmptyResp.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def PauseJob(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/Scheduler/PauseJob',
            scheduler__pb2.JobIdRequest.SerializeToString,
            scheduler__pb2.EmptyResp.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def ResumeJob(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/Scheduler/ResumeJob',
            scheduler__pb2.JobIdRequest.SerializeToString,
            scheduler__pb2.EmptyResp.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def RunJob(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/Scheduler/RunJob',
            scheduler__pb2.JobIdRequest.SerializeToString,
            scheduler__pb2.EmptyResp.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
