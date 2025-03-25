---
title: OpenTelemetry上手指南
date: 2024-12-02T11:53:08+08:00
slug: opentelemetry-getstarted
categories: 
- Engineering
featured: true
tags:
- Observability
---
## 可观测性的三要素

在现代分布式系统中，随着架构复杂性和微服务化的加剧，传统的监控手段已不足以应对系统运行状态的全面掌握。可观测性（Observability）作为一种新兴理念，旨在通过数据的采集和分析，帮助开发者、运维人员深入理解系统内部行为，确保系统健康和性能。可观测性通常由以下三大核心要素构成：

### Metrics（指标）

Metrics 是对系统性能和健康状态的量化描述，通常以数值形式呈现。这些数据通过定期采集，提供系统在特定时间点的运行快照，帮助用户快速了解系统的整体状况。

- **常见示例**：CPU 使用率（如 75%）、内存占用量（如 2GB/8GB）、请求速率（如每秒 100 次请求）、错误率（如 2% 的请求失败）等。
- **应用场景**：Metrics 通常与监控系统（如 Prometheus）结合，用于设置告警规则。例如，当错误率超过 5% 时触发告警通知。
- **特点**：Metrics 是高度聚合的数据，适合长期趋势分析，但缺乏请求级别的细节。

### Traces（追踪）

Traces 通过记录请求在分布式系统中的完整生命周期，揭示了请求从进入系统到离开的每一步路径。它特别适用于理解跨服务调用的复杂交互。

- **组成**：每个 Trace 由多个 Span 组成，Span 是请求在系统中某一个操作的执行记录（如调用数据库、发送 HTTP 请求等），包含开始时间、结束时间和元数据（如服务名称）。
- **实际用途**：例如，当用户访问一个电商网站下单时，Trace 可以展示从前端到支付服务、库存服务再到物流服务的调用链，快速定位延迟或错误的来源。
- **优势**：Traces 是调试分布式系统中性能瓶颈和故障的利器，尤其在微服务架构中尤为重要。

### Logs（日志）

Logs 是系统运行时生成的时间序列事件记录，提供系统行为的详细上下文。

- **形式**：日志可以是结构化的（如 JSON 格式，带有明确字段）或非结构化的（如纯文本）。结构化日志更易于查询和分析，例如：{"timestamp": "2025-02-25T10:00:00Z", "level": "INFO", "message": "User login successful"}。
- **用途**：Logs 是故障排查的基石。例如，当系统抛出 500 错误时，开发者可以通过日志查看具体的错误堆栈或异常信息。
- **与 Metrics 和 Traces 的关系**：Logs 提供细粒度的上下文，而 Metrics 提供宏观趋势，Traces 提供请求路径，三者相辅相成。

------

## OpenTelemetry：可观测性的统一标准

OpenTelemetry 是一个由 CNCF（云原生计算基金会）支持的开源项目，旨在为分布式系统提供一致、可移植的可观测性数据采集和传输框架。它由 OpenTracing 和 OpenCensus 两个项目合并发展而来，解决了之前标准不统一的问题。以下是 OpenTelemetry 的核心功能和优势：

- **统一的 API 和 SDK**：支持多种编程语言（如 Go、Java、Python 等），开发者只需集成一次即可采集 Metrics、Traces 和 Logs，无需为不同工具编写重复代码。
- **上下文自动传播**：在分布式系统中，OpenTelemetry 利用 W3C Trace Context 标准，自动在服务间传递追踪上下文，确保跨服务的 Trace 完整无缺。例如，一个请求从前端到后端，Trace ID 会贯穿始终。
- **广泛的后端支持**：支持将数据导出到多种可观测性平台，如 Prometheus（Metrics）、Jaeger（Traces）、Elasticsearch（Logs）等，提供灵活的选择。
- **高度可扩展性**：通过插件机制，开发者可以自定义数据采集逻辑，例如添加特定的业务指标或日志字段。

**注意事项**：OpenTelemetry 本身不负责数据的存储或可视化，它只是一个数据采集和传输的工具集。要实现完整可观测性，需要搭配后端平台（如本文使用的 OpenObserve）。

------

## Go 服务接入 OpenTelemetry 实践

接下来，我们将通过一个完整的示例，展示如何在 Go 服务中集成 OpenTelemetry，并结合 OpenObserve 实现可观测性。示例包括本地环境的搭建、OpenTelemetry Collector 的配置以及 Go 代码的埋点实践。

### 1. 启动本地 OpenObserve 服务

OpenObserve 是一个轻量级的可观测性平台，支持存储和可视化 Metrics、Traces 和 Logs。假设已安装 Docker，可以通过以下步骤启动：

```bash
docker run -v $PWD/data:/data -e ZO_DATA_DIR="/data" -p 5080:5080 \
    -e ZO_ROOT_USER_EMAIL="root@example.com" -e ZO_ROOT_USER_PASSWORD="Complexpass#123" \
    public.ecr.aws/zinclabs/openobserve:latest
```

- 参数说明
  - -v $PWD/data:/data：将本地目录挂载到容器，用于持久化存储数据。
  - -p 5080:5080：映射端口，使 OpenObserve 的 Web 界面可在本地访问。
  - ZO_ROOT_USER_EMAIL 和 ZO_ROOT_USER_PASSWORD：设置管理员账户。
- **验证**：启动后，打开浏览器访问 http://localhost:5080，使用 root@example.com 和 Complexpass#123 登录，检查仪表盘是否正常。

### 启动OpenTelemetry Collector服务

OpenTelemetry Collector 是一个独立的服务，负责接收、处理和导出可观测性数据。我们需要创建一个配置文件 otel-collector-config.yaml：
```yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
      http:
        endpoint: 0.0.0.0:4318

processors:
  batch:
    timeout: 1s
    send_batch_size: 1024

exporters:
  otlphttp/openobserve:
    endpoint: http://localhost:5080/api/default
    headers:
      Authorization: Basic bGVpQGNvbm5lY3RseS5haTphMldmRzFTWXlGWXhjUWtp
      stream-name: default

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [batch]
      exporters: [otlphttp/openobserve]
    metrics:
      receivers: [otlp]
      processors: [batch]
      exporters: [otlphttp/openobserve]
    logs:
      receivers: [otlp]
      processors: [batch]
      exporters: [otlphttp/openobserve]
```
**配置文件解析**：

- **Receivers**：使用 OTLP 协议（OpenTelemetry Protocol）接收数据，支持 gRPC 和 HTTP 两种方式。
- **Processors**：batch 处理器将数据批量处理，减少网络开销。
- **Exporters**：将数据发送到 OpenObserve，Authorization 使用 Base64 编码的用户名和密码（这里是示例值，实际使用时需替换）。

**启动 Collector**：使用 Docker Compose 启动服务，配置文件如下：

```yaml
services:
  otel-collector:
    image: otel/opentelemetry-collector-contrib:0.114.0
    volumes:
      - ./otel-collector-config.yaml:/etc/otelcol-contrib/config.yaml
      - /var/lib/docker/containers:/var/lib/docker/containers:ro
      - /var/log/containers:/var/log/containers:ro
    ports:
      # - 1888:1888 # pprof extension
      # - 18888:8888 # Prometheus metrics exposed by the Collector
      # - 18889:8889 # Prometheus exporter metrics
      # - 13133:13133 # health_check extension
      - 4317:4317 # OTLP gRPC receiver
      - 4318:4318 # OTLP http receiver
      # - 55679:55679 # zpages extension
volumes:
  data:
```

运行 docker-compose up 后，Collector 将监听 4317 和 4318 端口，接收数据并转发到 OpenObserve。

### Go代码埋点

以下是一个基于 Gin 框架的 Web 服务示例，展示如何集成 OpenTelemetry，采集 Metrics、Traces 和 Logs。服务包含两个端口：主服务（8080）和内部服务（18080），模拟分布式调用。

#### 初始化 OpenTelemetry

在 main.go 中初始化 Trace、Metric 和 Log 的 Provider：

```go
func initProvider() (func(), error) {
    ctx := context.Background()

    // 定义服务资源
    res, err := resource.New(ctx,
        resource.WithAttributes(
            semconv.ServiceName("my-service"),
            semconv.ServiceVersion("1.0.0"),
        ),
    )
    if err != nil {
        return nil, err
    }

    // 连接到 Collector
    conn, err := grpc.Dial("127.0.0.1:4317", grpc.WithTransportCredentials(insecure.NewCredentials()))
    if err != nil {
        return nil, err
    }

    // Trace exporter
    traceExporter, err := otlptracegrpc.New(ctx, otlptracegrpc.WithGRPCConn(conn))
    if err != nil {
        return nil, err
    }
    tracerProvider := sdktrace.NewTracerProvider(sdktrace.WithBatcher(traceExporter), sdktrace.WithResource(res))
    otel.SetTracerProvider(tracerProvider)

    // Metric exporter
    metricExporter, err := otlpmetricgrpc.New(ctx, otlpmetricgrpc.WithGRPCConn(conn))
    if err != nil {
        return nil, err
    }
    metricProvider := sdkmetric.NewMeterProvider(sdkmetric.WithResource(res), sdkmetric.WithReader(sdkmetric.NewPeriodicReader(metricExporter)))
    otel.SetMeterProvider(metricProvider)

    // Log exporter
    logExporter, err := otlploggrpc.New(ctx, otlploggrpc.WithGRPCConn(conn))
    if err != nil {
        return nil, err
    }
    logProvider := log.NewLoggerProvider(log.WithResource(res), log.WithProcessor(log.NewBatchProcessor(logExporter)))
    global.SetLoggerProvider(logProvider)

    return func() {
        tracerProvider.Shutdown(ctx)
        metricProvider.Shutdown(ctx)
        logProvider.Shutdown(ctx)
        conn.Close()
    }, nil
}
```

#### 添加 Metrics 中间件

使用中间件记录 HTTP 请求的延迟和计数：

```go
func metricsMiddleware() gin.HandlerFunc {
    meter := otel.GetMeterProvider().Meter("http_server")
    latencyHist, _ := meter.Float64Histogram("http_server_request_duration_seconds", metric.WithDescription("HTTP request duration"))
    requestCount, _ := meter.Int64Counter("http_server_requests_total", metric.WithDescription("Total HTTP requests"))

    return func(c *gin.Context) {
        start := time.Now()
        c.Next()
        duration := time.Since(start).Seconds()

        attrs := []attribute.KeyValue{
            attribute.String("method", c.Request.Method),
            attribute.String("path", c.FullPath()),
            attribute.Int("status", c.Writer.Status()),
        }
        latencyHist.Record(c.Request.Context(), duration, metric.WithAttributes(attrs...))
        requestCount.Add(c.Request.Context(), 1, metric.WithAttributes(attrs...))
    }
}
```

#### 主服务和内部服务

主服务监听 8080 端口，提供 /ping 和 /trace 两个端点。/trace 调用内部服务（18080 端口的 /hello）：

```go
func main() {
    cleanup, err := initProvider()
    if err != nil {
        panic(err)
    }
    defer cleanup()

    logger := zap.New(otelzap.NewCore("my-service", otelzap.WithLoggerProvider(global.GetLoggerProvider())))
    sugar := logger.Sugar()

    httpClient := &http.Client{Transport: otelhttp.NewTransport(http.DefaultTransport)}

    // 启动内部服务
    internalServer := newTracedServer(httpClient, sugar)
    go func() {
        if err := internalServer.Run(":18080"); err != nil {
            sugar.Errorw("internal server failed", "error", err)
        }
    }()

    // 主服务
    r := gin.New()
    r.Use(gin.Recovery(), metricsMiddleware())

    r.GET("/ping", func(c *gin.Context) {
        sugar.Infow("ping", "url", c.Request.URL.String(), "method", c.Request.Method)
        c.JSON(http.StatusOK, gin.H{"message": "pong"})
    })

    r.GET("/trace", func(c *gin.Context) {
        ctx := c.Request.Context()
        traceID := trace.SpanContextFromContext(ctx).TraceID().String()

        tr := otel.Tracer("time-consuming-operation")
        ctx, span := tr.Start(ctx, "sleep-operation")
        time.Sleep(1 * time.Second)
        span.End()

        req, _ := http.NewRequestWithContext(ctx, "GET", "http://localhost:18080/hello", nil)
        resp, err := httpClient.Do(req)
        if err != nil {
            sugar.Errorw("failed to send request", "error", err, "trace_id", traceID)
            c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
            return
        }
        defer resp.Body.Close()

        body, _ := io.ReadAll(resp.Body)
        var respBody map[string]any
        json.Unmarshal(body, &respBody)
        sugar.Infow("trace request completed", "trace_id", traceID, "status", resp.StatusCode)
        c.Header("X-Trace-ID", traceID)
        c.JSON(resp.StatusCode, respBody)
    })

    fmt.Println("Server started at :8080")
    panic(r.Run(":8080"))
}

func newTracedServer(httpClient *http.Client, sugar *zap.SugaredLogger) *gin.Engine {
    r := gin.New()
    r.Use(gin.Recovery())
    r.GET("/hello", func(c *gin.Context) {
        req, _ := http.NewRequestWithContext(c.Request.Context(), "GET", "https://api.github.com", nil)
        resp, err := httpClient.Do(req)
        if err != nil {
            sugar.Errorw("failed to send request", "error", err)
            c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
            return
        }
        defer resp.Body.Close()

        body, _ := io.ReadAll(resp.Body)
        var respBody map[string]any
        json.Unmarshal(body, &respBody)
        c.JSON(http.StatusOK, respBody)
    })
    return r
}
```



## 总结

通过本文的实践，我们展示了如何利用 OpenTelemetry 在 Go 服务中实现全面的可观测性：

1. **本地环境搭建**：启动 OpenObserve 和 OpenTelemetry Collector，为数据存储和处理奠定基础。
2. **组件初始化**：在 Go 中配置 Trace、Metric 和 Log 的 Provider，确保数据采集的完整性。
3. **指标收集**：通过中间件记录 HTTP 请求的性能数据，适合实时监控。
4. **链路追踪**：实现跨服务的请求追踪，定位分布式系统中的问题。
5. **日志集成**：结合 Zap 和 OpenTelemetry，输出结构化日志，便于故障排查。

未来，可以进一步探索以下方向：

- **高级可视化**：结合 Grafana Tempo 或 Jaeger，优化 Traces 的展示效果。
- **自动化告警**：基于 Metrics 配置动态阈值告警。
- **性能优化**：分析采集数据的开销，调整批量处理参数。

可观测性不仅是技术工具，更是现代系统设计的核心理念。通过 OpenTelemetry 和后端平台的结合，我们能够构建健壮、可维护的分布式系统。

## 参考链接

- [OpenTelemetry官方文档](https://opentelemetry.io/docs/)
- [OpenTelemetry Go SDK](https://github.com/open-telemetry/opentelemetry-go)
- [OpenObserve文档](https://openobserve.ai/docs/)
- [Gin Web Framework](https://gin-gonic.com/)
- [OpenTelemetry Collector](https://opentelemetry.io/docs/collector/)
- [Zap Logger](https://github.com/uber-go/zap)