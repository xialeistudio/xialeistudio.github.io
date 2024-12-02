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
在现代分布式系统中，可观测性是确保系统健康和性能的关键。可观测性通常由以下三要素组成：

**Metrics（指标）**
Metrics 是关于系统性能和健康的数值数据。它们通常是定期收集的，提供了系统在特定时间点的状态快照。
常见的指标包括 CPU 使用率、内存使用量、请求速率、错误率等。
Metrics 通常用于监控和告警。

**Traces（追踪）**
Traces 记录了请求在系统中流动的路径，帮助开发者理解请求的生命周期。
每个 trace 由多个 span 组成，每个 span 代表请求在系统中一个特定操作的执行。
Traces 对于调试分布式系统中的性能问题和瓶颈非常有用。

**Logs（日志）**
Logs 是系统在运行时生成的事件记录，通常包含时间戳和事件描述。
日志可以是结构化的（如 JSON 格式）或非结构化的（如纯文本）。
Logs 是调试和故障排查的基础工具。

## OpenTelemetry
OpenTelemetry 是一个开源项目，旨在为分布式系统提供统一的可观测性数据收集和传输标准。它是由 OpenTracing 和 OpenCensus 合并而来的，提供了以下功能：
- 统一的 API 和 SDK：支持多种编程语言，帮助开发者轻松集成可观测性。
- 自动化的上下文传播：在分布式系统中自动传播上下文信息，确保 trace 的完整性。
- 多种后端支持：支持将数据发送到多种后端，如 Prometheus、Jaeger、Zipkin 等。
- 可扩展性：通过插件和扩展机制，支持自定义数据收集和处理。

需要注意的是，OpenTelemetry 本身并不直接提供数据存储和分析功能，它只是一个标准和工具集，需要与具体的可观测性平台（如 Grafana、Jaeger、Prometheus 等）结合使用。
本文使用OpenObserve作为后端，OpenTelemetry作为数据收集工具进行演示。

## Go服务接入OpenTelemetry实践

### 启动本地OpenObserve服务
本地安装Docker后执行以下命令启动本地OpenObserve服务：
```bash
docker run -v $PWD/data:/data -e ZO_DATA_DIR="/data" -p 5080:5080 \
    -e ZO_ROOT_USER_EMAIL="root@example.com" -e ZO_ROOT_USER_PASSWORD="Complexpass#123" \
    public.ecr.aws/zinclabs/openobserve:latest
```

打开浏览器访问http://localhost:5080，使用root@example.com和Complexpass#123登录。
### 启动OpenTelemetry Collector服务

新建 `otel-collector-config.yaml` 文件，内容如下：
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
OpenTelemetry Collector由receiver、processor和exporter组成，receiver用于接收数据，processor用于处理数据，exporter用于将数据发送到后端。上述例子中，receiver使用otlp协议接收数据，processor使用batch进行批量处理，exporter将数据发送到OpenObserve。

使用下列配置通过Docker Compose启动OpenTelemetry Collector服务：
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

此时，OpenTelemetry Collector和OpenObserve服务已经启动，可以进行下一步。

### Go代码埋点

下面演示了一个Gin开发的Web服务器，访问主服务器的 `/hello` 路径时，会请求go协程启动的HTTP服务。

```go
package main

import (
	"context"
	"encoding/json"
	"fmt"
	"io"
	"math/rand"
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
	"go.opentelemetry.io/contrib/bridges/otelzap"
	"go.opentelemetry.io/contrib/instrumentation/net/http/otelhttp"
	"go.opentelemetry.io/otel"
	"go.opentelemetry.io/otel/attribute"
	"go.opentelemetry.io/otel/exporters/otlp/otlplog/otlploggrpc"
	"go.opentelemetry.io/otel/exporters/otlp/otlpmetric/otlpmetricgrpc"
	"go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracegrpc"
	"go.opentelemetry.io/otel/log/global"
	"go.opentelemetry.io/otel/metric"
	"go.opentelemetry.io/otel/sdk/log"
	sdkmetric "go.opentelemetry.io/otel/sdk/metric"
	"go.opentelemetry.io/otel/sdk/resource"
	sdktrace "go.opentelemetry.io/otel/sdk/trace"
	semconv "go.opentelemetry.io/otel/semconv/v1.21.0"
	"go.opentelemetry.io/otel/trace"
	"go.uber.org/zap"
	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"
)

func initProvider() (func(), error) {
	ctx := context.Background()

	res, err := resource.New(ctx,
		resource.WithAttributes(
			semconv.ServiceName("my-service"),
			semconv.ServiceVersion("1.0.0"),
		),
	)
	if err != nil {
		return nil, err
	}

	conn, err := grpc.Dial("127.0.0.1:4317",
		grpc.WithTransportCredentials(insecure.NewCredentials()),
		grpc.WithBlock(),
	)
	if err != nil {
		return nil, err
	}
	// 设置 trace exporter
	traceExporter, err := otlptracegrpc.New(ctx, otlptracegrpc.WithGRPCConn(conn))
	if err != nil {
		return nil, err
	}

	// 设置 trace provider
	tracerProvider := sdktrace.NewTracerProvider(
		sdktrace.WithBatcher(traceExporter),
		sdktrace.WithResource(res),
	)
	otel.SetTracerProvider(tracerProvider)
	// 设置 metric exporter
	metricExporter, err := otlpmetricgrpc.New(ctx, otlpmetricgrpc.WithGRPCConn(conn))
	if err != nil {
		return nil, err
	}

	// 设置 metric provider
	metricProvider := sdkmetric.NewMeterProvider(
		sdkmetric.WithResource(res),
		sdkmetric.WithReader(sdkmetric.NewPeriodicReader(metricExporter,
			sdkmetric.WithInterval(2*time.Second))),
	)
	otel.SetMeterProvider(metricProvider)

	// 设置log exporter
	logExporter, err := otlploggrpc.New(ctx, otlploggrpc.WithGRPCConn(conn))
	if err != nil {
		return nil, err
	}
	processor := log.NewBatchProcessor(logExporter, log.WithExportMaxBatchSize(10))
	logProvider := log.NewLoggerProvider(
		log.WithResource(res),
		log.WithProcessor(processor),
	)
	global.SetLoggerProvider(logProvider)

	return func() {
		ctx := context.Background()
		if err := tracerProvider.Shutdown(ctx); err != nil {
			panic(err)
		}
		if err := metricProvider.Shutdown(ctx); err != nil {
			panic(err)
		}
		if err := logProvider.Shutdown(ctx); err != nil {
			panic(err)
		}
		conn.Close()
	}, nil
}

func metricsMiddleware() gin.HandlerFunc {
	meter := otel.GetMeterProvider().Meter("http_server")
	// 创建延迟直方图
	latencyHist, _ := meter.Float64Histogram(
		"http_server_request_duration_seconds",
		metric.WithDescription("HTTP request duration in seconds"),
	)

	// 创建请求计数器
	requestCount, _ := meter.Int64Counter(
		"http_server_requests_total",
		metric.WithDescription("Total number of HTTP requests"),
	)

	return func(c *gin.Context) {
		start := time.Now()

		c.Next()

		duration := time.Since(start).Seconds()

		// 通用标签
		attrs := []attribute.KeyValue{
			attribute.String("method", c.Request.Method),
			attribute.String("path", c.FullPath()),
			attribute.Int("status", c.Writer.Status()),
		}

		// 记录指标，使用正确的 API
		latencyHist.Record(c.Request.Context(), duration, metric.WithAttributes(attrs...))
		requestCount.Add(c.Request.Context(), 1, metric.WithAttributes(attrs...))
	}
}

func newTracedServer(httpClient *http.Client, sugar *zap.SugaredLogger) *gin.Engine {
	// 为内部服务创建新的 resource
	res, err := resource.New(context.Background(),
		resource.WithAttributes(
			semconv.ServiceName("helloservice"),
			semconv.ServiceVersion("1.0.0"),
		),
	)
	if err != nil {
		sugar.Errorw("failed to create resource", "error", err)
		panic(err)
	}

	// 为内部服务创建新的 TracerProvider
	tracerProvider := sdktrace.NewTracerProvider(
		sdktrace.WithResource(res),
	)

	r := gin.New()
	r.Use(gin.Recovery())

	// 使用新的 TracerProvider 创建 handler
	r.Use(func(c *gin.Context) {
		handler := otelhttp.NewHandler(
			http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
				c.Request = r
				c.Next()
			}),
			"helloservice.http",
			otelhttp.WithTracerProvider(tracerProvider),
		)
		handler.ServeHTTP(c.Writer, c.Request)
	})

	r.GET("/hello", func(c *gin.Context) {
		// 从请求中获取 trace context
		ctx := c.Request.Context()

		// 创建 GitHub API 请求
		req, err := http.NewRequestWithContext(ctx, "GET", "https://api.github.com", nil)
		if err != nil {
			sugar.Errorw("failed to create request", "error", err)
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}

		// 发送请求
		resp, err := httpClient.Do(req)
		if err != nil {
			sugar.Errorw("failed to send request", "error", err)
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}
		defer resp.Body.Close()

		// 读取响应
		body, err := io.ReadAll(resp.Body)
		if err != nil {
			sugar.Errorw("failed to read response", "error", err)
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}

		var respBody map[string]any
		if err := json.Unmarshal(body, &respBody); err != nil {
			sugar.Errorw("failed to unmarshal response", "error", err)
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}

		c.JSON(http.StatusOK, respBody)
	})

	return r
}

func main() {
	cleanup, err := initProvider()
	if err != nil {
		panic(err)
	}
	defer cleanup()

	// 创建 OTLP core
	logProvider := global.GetLoggerProvider()
	logger := zap.New(otelzap.NewCore("my/pkg/name", otelzap.WithLoggerProvider(logProvider)))
	defer logger.Sync()
	sugar := logger.Sugar()

	// 创建带有 trace 的 HTTP 客户端
	httpClient := &http.Client{
		Transport: otelhttp.NewTransport(http.DefaultTransport),
	}

	// 启动内部服务器（18080端口）
	internalServer := newTracedServer(httpClient, sugar)
	go func() {
		if err := internalServer.Run(":18080"); err != nil {
			sugar.Errorw("internal server failed", "error", err)
		}
	}()

	// 主服务器配置
	gin.SetMode(gin.ReleaseMode)
	r := gin.New()
	r.Use(gin.Recovery(), metricsMiddleware())

	r.GET("/ping", func(c *gin.Context) {
		resp := gin.H{
			"message": "pong",
		}
		sugar.Infow("ping",
			"url", c.Request.URL.String(),
			"method", c.Request.Method,
			"ip", c.ClientIP(),
			"user-agent", c.Request.UserAgent(),
			"resp", resp,
		)
		c.JSON(http.StatusOK, resp)
	})

	r.GET("/github", func(c *gin.Context) {
		// 从 gin.Context 获取 trace context
		ctx := c.Request.Context()

		// 创建新的请求
		req, err := http.NewRequestWithContext(ctx, "GET", "https://api.github.com", nil)
		if err != nil {
			sugar.Errorw("failed to create request",
				"error", err,
			)
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}

		// 发送请求
		resp, err := httpClient.Do(req)
		if err != nil {
			sugar.Errorw("failed to send request",
				"error", err,
			)
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}
		defer resp.Body.Close()

		// 读取响应
		body, err := io.ReadAll(resp.Body)
		if err != nil {
			sugar.Errorw("failed to read response",
				"error", err,
			)
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}

		var respBody map[string]any
		if err := json.Unmarshal(body, &respBody); err != nil {
			sugar.Errorw("failed to unmarshal response",
				"error", err,
			)
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}

		// 记录日志
		sugar.Infow("github api request",
			zap.Any("resp", map[string]any{"status": rand.Intn(500)}),
		)

		// 返回响应
		c.JSON(resp.StatusCode, respBody)
	})

	// 添加 /trace 路由
	r.GET("/trace", func(c *gin.Context) {
		ctx := c.Request.Context()

		// 获取 trace ID 用于日志
		var traceID string
		if spanCtx := trace.SpanContextFromContext(ctx); spanCtx.IsValid() {
			traceID = spanCtx.TraceID().String()
		}

		tr := otel.Tracer("time-consuming-operation")
		ctx, span := tr.Start(ctx, "sleep-operation")
		time.Sleep(1 * time.Second)
		span.End()

		req, err := http.NewRequestWithContext(ctx, "GET", "http://localhost:18080/hello", nil)
		if err != nil {
			sugar.Errorw("failed to create request",
				"error", err,
				"trace_id", traceID,
			)
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}

		resp, err := httpClient.Do(req)
		if err != nil {
			sugar.Errorw("failed to send request",
				"error", err,
				"trace_id", traceID,
			)
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}
		defer resp.Body.Close()

		body, err := io.ReadAll(resp.Body)
		if err != nil {
			sugar.Errorw("failed to read response",
				"error", err,
				"trace_id", traceID,
			)
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}

		var respBody map[string]any
		if err := json.Unmarshal(body, &respBody); err != nil {
			sugar.Errorw("failed to unmarshal response",
				"error", err,
				"trace_id", traceID,
			)
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}

		// 记录成功日志
		sugar.Infow("trace request completed",
			"trace_id", traceID,
			"status", resp.StatusCode,
		)

		// 设置响应头
		if traceID != "" {
			c.Header("X-Trace-ID", traceID)
		}

		c.JSON(resp.StatusCode, respBody)
	})

	fmt.Println("start server")
	panic(r.Run(":8080"))
}
```

## 总结

本文详细介绍了OpenTelemetry在Go服务中的实践应用。通过可观测性的三大支柱（Metrics、Traces和Logs），我们可以全方位监控和了解分布式系统的运行状态。OpenTelemetry作为一个统一的可观测性框架，不仅提供了标准化的数据收集方式，还支持多种后端存储方案。

在实践部分，我们通过一个完整的示例展示了：
1. 如何搭建本地OpenObserve和OpenTelemetry Collector环境
2. 如何在Go服务中初始化OpenTelemetry的各个组件
3. 如何使用中间件收集HTTP请求的指标
4. 如何在分布式系统中进行链路追踪
5. 如何集成结构化日志

通过这些实践，我们可以构建一个具有完整可观测性的现代分布式系统，为系统的监控、调试和优化提供有力支持。

## 参考链接

- [OpenTelemetry官方文档](https://opentelemetry.io/docs/)
- [OpenTelemetry Go SDK](https://github.com/open-telemetry/opentelemetry-go)
- [OpenObserve文档](https://openobserve.ai/docs/)
- [Gin Web Framework](https://gin-gonic.com/)
- [OpenTelemetry Collector](https://opentelemetry.io/docs/collector/)
- [Zap Logger](https://github.com/uber-go/zap)