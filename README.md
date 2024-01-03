# zero-grpc

zero-grpc是一个可以方便的使用grpc服务的框架。

## 安装

```shell
pip install zero-grpc
```

## 快速开始

### proto文件生成python代码

首先准备一个proto文件，我们给他这个文件命名为`example.proto`

```protobuf
syntax = "proto3";

service Example {
    rpc GrpcExample (Request) returns (Response);
}

message Request {}

message Response {
    string message = 1;
}
```

然后我们使用grpc提供的命令生成proto文件对应的python代码，以下命令是获取当前目录下的`example.proto`
文件解析，然后生成的对应的python代码同样放在当前目录下。

```shell
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. example.proto
```

如果你觉得命令不太好记，也没有关系，`zero-grpc`提供了相关的命令，你只需要输入以下命令即可实现上面的命令的相同效果。

注意的地方
- 不管是上述命令还是`zero-grpc`提供的命令都中proto文件都不可以是完整的地址，只能是相对地址。
- 如果你执行`zero-grpc`的命令行提示没有安装`grpc-tools`这个包，并不一定是你当前`venv`环境中没有安装，可能是你最外层的python环境中没有安装这个包，所以跳出当前的`venv`环境去最外层安装即可继续执行命令。

```shell
zero proto2code --file=example.proto
```

### 使用zero-grpc创建一个grpc服务

```python
import example_pb2
import example_pb2_grpc

from zero import Zero

app = Zero(__name__)
app.add_service(example_pb2, example_pb2_grpc)


@app.rpc(name='/Example/GrpcExample')
def index(self, request, context):
    return self.srv.Response(message='hello zero-grpc')


if __name__ == '__main__':
    app.run()
```
