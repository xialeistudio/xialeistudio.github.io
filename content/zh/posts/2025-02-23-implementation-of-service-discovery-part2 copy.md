---
title: 服务发现的设计与实现（二）
date: 2025-02-23T11:53:08+08:00
slug: implementation-of-service-discovery-part2
categories: 
- Engineering
featured: true
tags:
- Microservices
---

在微服务架构中，服务发现是确保服务间高效通信和动态扩展的关键机制。随着分布式系统的复杂性日益增加，如何设计一个可靠、高性能的服务发现方案成为工程实践中的核心课题。

本文作为“服务发现的设计与实现”系列的第二部分，将深入探讨服务注册中心的具体实现与负载均衡策略。我们将聚焦于三种主流技术——etcd、Consul 和 ZooKeeper，分析它们的原理与应用场景，并通过实际代码展示如何构建服务发现功能。此外，我们还将介绍常见的负载均衡算法及其实现方法，帮助读者理解如何在微服务中优化请求分配。 
<!--more-->

## Consul注册中心

Consul 是一个开源的服务网格解决方案，提供服务发现、配置和分段功能。它结合了分布式系统的几个关键组件，包括服务发现、健康检查、键值存储和多数据中心支持。Consul 的设计目标是提供一种简单、灵活且可靠的方法来构建和运行分布式系统。

Consul 的核心特性包括一个分布式服务目录，它允许服务实例注册自己并提供元数据，其他服务可以通过查询这个目录来发现它们。它还提供了健康检查功能，可以确保只有健康的服务实例被客户端发现。此外，Consul 提供了一个内置的 DNS 和 HTTP API 接口，用于服务发现，使得服务之间的通信变得简单。

Consul 还支持分布式一致性配置，允许团队存储和同步配置信息。它的分段特性允许服务在不同的网络环境中进行隔离，这对于微服务架构中的蓝绿部署和金丝雀发布非常有用。

Consul 的架构设计支持高可用性，它使用 Raft 算法来保证数据的一致性和容错性。Consul 通常部署为一个集群模式，集群中的每个节点都参与数据的复制和一致性保证。这种设计使得 Consul 成为构建现代云原生应用的有力工具，尤其是在需要跨多个数据中心或云环境进行服务发现和配置管理的场景中。

### Consul 的安装和启动

要开始使用 Consul 作为服务注册中心，首先需要安装 Consul。您可以访问 HashiCorp 官方开发者网站 [https://developer.hashicorp.com/consul/install](https://developer.hashicorp.com/consul/install) 下载与您的操作系统相匹配的 Consul 二进制文件。

安装完成后，打开终端并运行以下命令来启动 Consul 的开发服务器模式。这将启动一个单节点的 Consul 服务器，适用于开发和测试环境。

```bash
consul agent -dev -bind 127.0.0.1
```

接下来，在新的终端会话中，您可以使用以下命令来设置一个键值对。此命令将存储一个简单的字符串值，并返回操作结果。如果操作成功，您应该看到 "true" 作为输出。

```bash
curl \
  --request PUT \
  --data 'hello consul' \
  http://127.0.0.1:8500/v1/kv/foo
```

最后，为了验证键值对是否已正确设置，您可以执行以下命令来检索该键的值。预期的输出将显示键 "foo" 及其关联的值，值将以 Base64 编码的形式展示。

```
curl http://127.0.0.1:8500/v1/kv/foo
```

预期的输出结果如下，展示了键 "foo" 的详细信息，包括其值 "aGVsbG8gY29uc3Vs"（Base64 编码的 "hello consul"）：

```json
[
  {
    "LockIndex": 0,
    "Key": "foo",
    "Flags": 0,
    "Value": "aGVsbG8gY29uc3Vs",
    "CreateIndex": 24,
    "ModifyIndex": 24
  }
]
```

### 包结构设计

我们直接在上一节的基础上添加 consul 包即可。

```
├── client
│   └── client.go
├── discovery
│   ├── discovery.go
│   └── etcd
│       ├── registry.go
│       └── registry_test.go
│   └── consul
│       ├── registry.go
│       └── registry_test.go
├── go.mod
└── loadbalancer
    └── loadbalancer.go
```

### 编写实现

Consul 服务发现客户端的逻辑和 etcd 类似，都是提供获取节点、注册服务实例、取消注册服务实例。不同的是 Consul 的 watch 机制和 etcd 不同，而且 Consul 支持健康检查。

**discovery/consul/registry.go**

```go
package consul

import (
    "context"
    "fmt"
    "log"
    "net"
    "sync"

    capi "github.com/hashicorp/consul/api"
    "github.com/hashicorp/consul/api/watch"
    "github.com/xialeistudio/go-service-discovery/discovery"
)

type registry struct {
    nodeListMap *sync.Map // <serviceName, <nodeKey, *ServiceNode>>
    config      *capi.Config
    client      *capi.Client
}

func (r *registry) GetNodes(ctx context.Context, serviceName string, tags map[string]string) ([]*discovery.ServiceNode, error) {
    nodes, exists := r.nodeListMap.Load(serviceName)
    if !exists {
        var err error
        // 本地缓存为空，从 consul 拉取
        nodes, err = r.pullNodes(ctx, serviceName)
        if err != nil {
            return nil, err
        }
        // 缓存到本地
        r.nodeListMap.Store(serviceName, nodes)
        // 启动 watch
        go r.watchNodes(serviceName)
    }
    // 按标签过滤节点
    var filteredNodes []*discovery.ServiceNode
    nodes.(*sync.Map).Range(func(key, value interface{}) bool {
        node := value.(*discovery.ServiceNode)
        if discovery.MatchTags(node.Tags, tags) {
            filteredNodes = append(filteredNodes, node)
        }
        return true
    })
    return filteredNodes, nil
}

func (r *registry) Register(ctx context.Context, node *discovery.ServiceNode) error {
    service := &capi.AgentServiceRegistration{
        ID:      makeNodeKey(node),
        Name:    node.ServiceName,
        Address: node.IP.String(),
        Port:    node.Port,
        Meta:    node.Tags,
        Check: &capi.AgentServiceCheck{ // 健康检查
            TCP:                            fmt.Sprintf("%s:%d", node.IP.String(), node.Port),
            Timeout:                        "5s",
            Interval:                       "5s",
            DeregisterCriticalServiceAfter: "30s",
            Status:                         capi.HealthPassing,
        },
    }
    err := r.client.Agent().ServiceRegisterOpts(service, capi.ServiceRegisterOpts{}.WithContext(ctx))
    if err != nil {
        return fmt.Errorf("register service error: %w", err)
    }
    return nil
}

func (r *registry) Unregister(ctx context.Context, node *discovery.ServiceNode) error {
    opts := &capi.QueryOptions{}
    opts = opts.WithContext(ctx)
    err := r.client.Agent().ServiceDeregisterOpts(makeNodeKey(node), opts)
    if err != nil {
        return fmt.Errorf("unregister service error: %w", err)
    }
    return nil
}

func (r *registry) pullNodes(ctx context.Context, name string) (*sync.Map, error) {
    opts := &capi.QueryOptions{}
    opts = opts.WithContext(ctx)
    services, err := r.client.Agent().ServicesWithFilterOpts(fmt.Sprintf(`Service=="%s"`, name), opts)
    if err != nil {
        return nil, fmt.Errorf("pull services error: %w", err)
    }
    var results sync.Map
    for _, service := range services {
        node := &discovery.ServiceNode{
            ServiceName: name,
            IP:          net.ParseIP(service.Address),
            Port:        service.Port,
            Tags:        service.Meta,
        }
        results.Store(makeNodeKey(node), node)
    }
    return &results, nil
}

func (r *registry) watchNodes(name string) {
    params := map[string]any{
        "type":    "service",
        "service": name,
    }
    plan, _ := watch.Parse(params)
    plan.Handler = func(u uint64, i interface{}) {
        if i == nil {
            return
        }
        val, ok := i.([]*capi.ServiceEntry)
        if !ok {
            return
        }
        if len(val) == 0 {
            r.nodeListMap.Store(name, &sync.Map{})
            return
        }
        var (
            healthInstances sync.Map
        )
        for _, instance := range val {
            if instance.Service.Service != name {
                continue
            }
            if instance.Checks.AggregatedStatus() == capi.HealthPassing {
                node := &discovery.ServiceNode{
                    ServiceName: name,
                    IP:          net.ParseIP(instance.Service.Address),
                    Port:        instance.Service.Port,
                    Tags:        instance.Service.Meta,
                }
                healthInstances.Store(makeNodeKey(node), node)
            }
        }
        r.nodeListMap.Store(name, &healthInstances)
    }
    defer plan.Stop()
    if err := plan.Run(r.config.Address); err != nil {
        log.Printf("watch service %s error: %v", name, err)
    }
}

func NewRegistry(config *capi.Config) (discovery.NodeRegistry, error) {
    client, err := capi.NewClient(config)
    if err != nil {
        return nil, fmt.Errorf("new consul client error: %w", err)
    }
    return &registry{
        nodeListMap: new(sync.Map),
        client:      client,
        config:      config,
    }, nil
}

func makeNodeKey(node *discovery.ServiceNode) string {
    return fmt.Sprintf("%s/%s:%d", node.ServiceName, node.IP.String(), node.Port)
}
```

watch 机制允许客户端实时监听服务状态的变化。在上述代码中，watchNodes 函数实现了对 Consul 服务状态的监听，当服务注册或注销时，通过 handler 更新本地缓存，确保服务消费者能够获取到最新的服务节点列表。这种机制使得服务消费者能够及时响应服务提供者的变化，提高了系统的动态性和可靠性。

而健康检查确保只有健康的服务实例对消费者可见，上述代码使用 TCP 连接来进行健康检查。一旦服务实例出现问题，Consul 会自动将其标记为不健康，并从服务发现中移除，避免流量被路由到该实例。

### 单元测试编写

因为我们使用了面向接口的方式来设计注册中心，前面的 etcd 和当前的 Consul 都只是实现类，因此单元测试可以通用，唯一不同的是初始化 Registry 的代码。

**discovery/consul/registry_test.go**

```go
package consul

import (
    "context"
    "net"
    "testing"
    "time"

    capi "github.com/hashicorp/consul/api"
    json "github.com/json-iterator/go"
    "github.com/stretchr/testify/assert"
    "github.com/xialeistudio/go-service-discovery/discovery"
)

func TestConsulRegistry(t *testing.T) {
    a := assert.New(t)
    // 初始化注册中心
    r, err := NewRegistry(&capi.Config{
        Address: "localhost:8500",
    })
    a.Nil(err)

    t.Run("Register single node", func(t *testing.T) {
        node := &discovery.ServiceNode{
            ServiceName: "test",
            IP:          net.IPv4(127, 0, 0, 1),
            Port:        8484,
            Tags: map[string]string{
                "version": "1.0",
            },
        }
        // 注册节点
        err = r.Register(context.Background(), node)
        a.Nil(err)
        time.Sleep(time.Millisecond * 100)
        // 获取节点
        nodes, err := r.GetNodes(context.Background(), "test", map[string]string{
            "version": "1.0",
        })
        a.Nil(err)
        a.Len(nodes, 1)
        a.Equal(node, nodes[0])
        // 注销节点
        err = r.Unregister(context.Background(), node)
        a.Nil(err)
        time.Sleep(time.Millisecond * 100)
        // 获取节点
        nodes, err = r.GetNodes(context.Background(), "test", map[string]string{
            "version": "1.0",
        })
        a.Nil(err)
        a.Len(nodes, 0)
    })

    t.Run("Register multi nodeListMap with multi tags", func(t *testing.T) {
        node1 := &discovery.ServiceNode{
            ServiceName: "test",
            IP:          net.IPv4(127, 0, 0, 1),
            Port:        8484,
            Tags: map[string]string{
                "version": "1.0",
                "region":  "cn",
            },
        }
        node2 := &discovery.ServiceNode{
            ServiceName: "test",
            IP:          net.IPv4(127, 0, 0, 2),
            Port:        8484,
            Tags: map[string]string{
                "version": "1.0",
                "region":  "us",
            },
        }
        // 注册节点
        err = r.Register(context.Background(), node1)
        a.Nil(err)
        err = r.Register(context.Background(), node2)
        a.Nil(err)
        time.Sleep(time.Millisecond * 100)
        // 获取节点
        nodes, err := r.GetNodes(context.Background(), "test", map[string]string{
            "version": "1.0",
            "region":  "cn",
        })
        a.Nil(err)
        a.Len(nodes, 1)
        str, _ := json.MarshalToString(nodes)
        t.Log(str)
        a.Equal(node1, nodes[0])
        // 获取节点
        nodes, err = r.GetNodes(context.Background(), "test", map[string]string{
            "version": "1.0",
            "region":  "us",
        })
        a.Nil(err)
        a.Len(nodes, 1)
        a.Equal(node2, nodes[0])
        // 获取节点
        nodes, err = r.GetNodes(context.Background(), "test", nil)
        a.Nil(err)
        a.Len(nodes, 2)
        // 注销节点
        err = r.Unregister(context.Background(), node1)
        a.Nil(err)
        err = r.Unregister(context.Background(), node2)
        a.Nil(err)
        time.Sleep(time.Millisecond * 100)
        // 获取节点
        nodes, err = r.GetNodes(context.Background(), "test", map[string]string{
            "version": "1.0",
        })
        a.Nil(err)
        a.Len(nodes, 0)
    })
}
```

在确保 Consul 服务端运行的情况下执行单元测试即可。

Consul 作为服务注册与发现的工具，在微服务架构中扮演着至关重要的角色。它通过提供一个中心化的服务注册表，使得服务实例能够相互发现并进行通信。服务注册过程中，每个服务实例将自己注册到 Consul，并关联健康检查以确保其可用性。Consul 的 watch 机制允许服务消费者实时监听服务状态的变化，从而动态更新本地服务节点列表。这种动态服务发现的能力，不仅提高了系统的灵活性和可扩展性，还增强了服务之间的解耦合。Consul 的这些特性共同确保了微服务架构的高效运行和稳定性，使其成为现代云原生应用的理想选择。

## Zookeeper注册中心

ZooKeeper 是一个分布式协调服务，它为分布式应用提供一致性协调功能。作为一个开源的协调服务，ZooKeeper 提供了一系列的原语，使得开发者能够构建可靠的分布式同步服务。

ZooKeeper 的核心是它的状态机模型，它维护了一个具有层次结构的命名空间，类似于文件系统的树形结构。每个节点在这个命名空间中被称为 znode，它可以存储数据和状态信息。客户端可以通过创建、读取、更新和删除这些 znode 来实现服务的注册与发现。

在微服务架构中，ZooKeeper 常被用作服务注册中心，服务实例在启动时会在 ZooKeeper 中注册自己的信息，如 IP 地址和端口号。其他服务实例可以通过查询这些 znode 来发现可用的服务提供者。此外，ZooKeeper 还提供了 watch 机制，允许服务实例监听 znode 的变化，从而实现服务的动态发现和负载均衡。

### ZooKeeper 的安装和启动

ZooKeeper 作为基于 Java 的分布式协调服务，其运行离不开 Java 环境的支持。因此，首先需要确保您的系统中安装了 JDK 或 JRE。您可以通过访问 [https://www.java.com/zh-CN/download/help/download_options_zh-cn.html](https://www.java.com/zh-CN/download/help/download_options_zh-cn.html) 下载与您的操作系统相匹配的 Java 版本，并进行安装。

安装完成后，您可以通过打开终端或命令提示符，输入以下命令来验证 Java 是否安装成功：

```bash
java -version
```

例如，笔者的系统中显示的输出如下：

```
openjdk version "17.0.9" 2023-10-17
OpenJDK Runtime Environment Homebrew (build 17.0.9+0)
OpenJDK 64-Bit Server VM Homebrew (build 17.0.9+0, mixed mode, sharing)
```

接下来，您可以访问 https://zookeeper.apache.org/releases.html 下载最新版本的 ZooKeeper，并按照提供的指南进行解压和配置。

启动 ZooKeeper 服务时，您可以在终端执行以下命令，以在前台模式运行 ZooKeeper，这样有助于实时查看服务的输出信息：

```bash
zkServer start-foreground
```

为了与 ZooKeeper 服务器建立连接，您可以在新的终端会话中执行以下命令：

```bash
zkCli
```

一旦连接成功，您可以通过执行 stat / 命令来查看根节点的状态。以下是笔者的示例输出：

```
[zk: localhost:2181(CONNECTED) 1] stat /
cZxid = 0x0
ctime = Thu Jan 01 08:00:00 CST 1970
mZxid = 0x0
mtime = Thu Jan 01 08:00:00 CST 1970
pZxid = 0x3a
cversion = 27
dataVersion = 0
aclVersion = 0
ephemeralOwner = 0x0
dataLength = 0
numChildren = 1
```

至此，我们已经成功安装并启动了 ZooKeeper 服务器，并且能够通过命令行界面与其交互。

### 编写实现

ZooKeeper 需要先建立父路径之后才能添加服务实例节点，因此需要先创建根路径 /services，在注册服务节点之前确保服务名称节点已经创建，最后创建服务实例节点即可。

我们使用的 watch 机制是接收到节点事件后尝试获取节点详情数据，如果获取不到则证明节点被删除，需要跳过循环，不能直接 return，否则会导致本地缓存无法更新。

**discovery/zookeeper/registry.go**

```go
package zookeeper

import (
    "context"
    "errors"
    "fmt"
    "sync"
    "time"

    "github.com/go-zookeeper/zk"
    json "github.com/json-iterator/go"
    "github.com/xialeistudio/go-service-discovery/discovery"
)

var (
    // DialTimeout 默认的连接超时时间
    DialTimeout = 5 * time.Second
    // BasePath 服务注册的根路径
    BasePath = "/services"
)

type registry struct {
    nodeListMap *sync.Map // <serviceName, <nodeKey, *ServiceNode>>
    conn        *zk.Conn
}

func (r *registry) GetNodes(ctx context.Context, serviceName string, tags map[string]string) ([]*discovery.ServiceNode, error) {
    nodes, exists := r.nodeListMap.Load(serviceName)
    if !exists {
        var err error
        // 本地缓存为空，从 zookeeper 拉取
        nodes, err = r.pullNodes(ctx, serviceName)
        if err != nil {
            return nil, err
        }
        // 缓存到本地
        r.nodeListMap.Store(serviceName, nodes)
        // 启动 watch
        go r.watchNodes(serviceName)
    }
    // 按标签过滤节点
    var filteredNodes []*discovery.ServiceNode
    nodes.(*sync.Map).Range(func(key, value interface{}) bool {
        node := value.(*discovery.ServiceNode)
        if discovery.MatchTags(node.Tags, tags) {
            filteredNodes = append(filteredNodes, node)
        }
        return true
    })
    return filteredNodes, nil
}

func (r *registry) Register(_ context.Context, node *discovery.ServiceNode) error {
    if err := r.ensureServiceNode(node.ServiceName); err != nil {
        return err
    }
    data, err := json.Marshal(node)
    if err != nil {
        return fmt.Errorf("failed to marshal node: %v", err)
    }
    nodePath := fmt.Sprintf("%s/%s", makeServicePath(node.ServiceName), makeNodeKey(node))
    _, err = r.conn.Create(nodePath, data, zk.FlagEphemeral, zk.WorldACL(zk.PermAll))
    if err != nil {
        return fmt.Errorf("failed to create node %v: %v", node, err)
    }
    return nil
}

func makeNodeKey(node *discovery.ServiceNode) string {
    return fmt.Sprintf("%s:%d", node.IP.String(), node.Port)
}

func (r *registry) Unregister(_ context.Context, node *discovery.ServiceNode) error {
    nodePath := fmt.Sprintf("%s/%s", makeServicePath(node.ServiceName), makeNodeKey(node))
    err := r.conn.Delete(nodePath, -1)
    if err != nil {
        return fmt.Errorf("failed to delete node %v: %v", node, err)
    }
    return nil
}

func (r *registry) ensureServiceNode(name string) error {
    nodePath := makeServicePath(name)
    exists, _, err := r.conn.Exists(nodePath)
    if err != nil {
        return fmt.Errorf("failed to check if node exists %v: %v", nodePath, err)
    }
    if !exists {
        _, err = r.conn.Create(nodePath, nil, zk.FlagPersistent, zk.WorldACL(zk.PermAll))
        if err != nil {
            return fmt.Errorf("failed to create node %v: %v", nodePath, err)
        }
    }
    return nil
}

func (r *registry) pullNodes(_ context.Context, serviceName string) (*sync.Map, error) {
    var nodes sync.Map
    nodePath := makeServicePath(serviceName)
    children, _, err := r.conn.Children(nodePath)
    if err != nil {
        return nil, fmt.Errorf("failed to get children of node %v: %v", nodePath, err)
    }
    for _, child := range children {
        data, _, err := r.conn.Get(fmt.Sprintf("%s/%s", nodePath, child))
        if err != nil {
            return nil, fmt.Errorf("failed to get node %v: %v", child, err)
        }
        var node discovery.ServiceNode
        if err := json.Unmarshal(data, &node); err != nil {
            return nil, fmt.Errorf("failed to unmarshal node %v: %v", child, err)
        }
        nodes.Store(child, &node)
    }
    return &nodes, nil
}

func makeServicePath(serviceName string) string {
    return fmt.Sprintf("%s/%s", BasePath, serviceName)
}

func (r *registry) watchNodes(name string) {
    nodePath := makeServicePath(name)
    for {
        children, _, ch, err := r.conn.ChildrenW(nodePath)
        if err != nil {
            fmt.Printf("failed to watch children of node %s: %v\n", nodePath, err)
            return
        }
        var nodes sync.Map
        var count int
        for _, child := range children {
            data, _, err := r.conn.Get(fmt.Sprintf("%s/%s", nodePath, child))
            if err != nil { // 如果是节点解除注册触发的事件，此处无法获取到节点数据，直接跳过即可，不能报错，否则无法更新本地节点
                continue
            }
            var node discovery.ServiceNode
            if err := json.Unmarshal(data, &node); err != nil {
                fmt.Printf("failed to unmarshal node %s: %v\n", child, err)
                return
            }
            count++
            nodes.Store(child, &node)
        }
        r.nodeListMap.Store(name, &nodes)
        select {
        case <-ch:
        }
    }
}

func NewRegistry(servers []string) (discovery.NodeRegistry, error) {
    conn, _, err := zk.Connect(servers, DialTimeout)
    if err != nil {
        return nil, fmt.Errorf("failed to connect to zookeeper: %v", err)
    }
    // create base path
    _, err = conn.Create(BasePath, nil, 0, zk.WorldACL(zk.PermAll))
    if err != nil && !errors.Is(err, zk.ErrNodeExists) {
        return nil, fmt.Errorf("failed to create base path %v: %v", BasePath, err)
    }
    return &registry{
        nodeListMap: &sync.Map{},
        conn:        conn,
    }, nil
}
```

在 ZooKeeper 中，只有永久节点下面可以创建临时节点，因此服务名称节点是永久性的，而服务实例节点是临时的。当注册服务的节点与 ZooKeeper 服务器的连接断开时，临时节点会自动被删除。

### 单元测试

单元测试代码与 etcd 和 consul 一致，唯一的区别是初始化 Registry 的代码：

**discovery/zookeeper/registry_test.go**

```go
r, err := NewRegistry([]string{"localhost:2181"})
a.Nil(err)
```

ZooKeeper 是一个高性能的分布式协调服务，它为构建大型分布式系统提供了关键的协调功能。作为一个服务注册中心，ZooKeeper 能够存储服务实例的信息，并允许服务消费者查询和订阅这些信息。它的树形结构使得服务的注册和发现变得直观和灵活。ZooKeeper 的临时节点和 watch 机制进一步增强了服务注册中心的能力，确保了服务实例的动态管理和自动更新。这些特性使得 ZooKeeper 成为微服务架构中服务发现和协调的理想选择，尤其是在需要强一致性和高可靠性的场景中。

## 4.5 负载均衡

在微服务架构中，服务调用的负载均衡是一个至关重要的环节，它决定了如何将大量的服务请求有效地分配到多个服务实例上。良好的负载均衡策略可以显著提高系统的吞吐量、响应速度和整体的可靠性。本节将深入探讨负载均衡的原理和实现，介绍几种常见的负载均衡算法，包括轮询、随机、加权轮询等，以及它们在实际应用中的适用场景和实现方式。

### 原理

负载均衡本质上是从一组服务节点中选择一个节点来处理客户端的请求。这个过程通过算法决定哪个节点应该接收特定的请求，目的是确保所有节点的负载尽可能均衡，从而提高系统的整体性能和可靠性。负载均衡器根据预设的策略，如轮询、随机选择或最少连接数，智能地分发请求，避免任何单一节点因过载而影响服务的稳定性。

### 轮询实现

轮询（Round Robin）负载均衡策略通过循环遍历服务节点列表，依次将新的请求分配给每个可用的服务实例。这种顺序分配方法简单而公平，确保了所有节点在长时间内接收到的请求数量大致相等，有效地平衡了系统负载，提高了资源利用率。轮询策略尤其适合所有服务节点性能相近的场景。

`loadbalancer/round_robin.go`

```go
package loadbalancer

import (
    "github.com/xialeistudio/go-service-discovery/discovery"
)

type roundRobin struct {
    index int
}

func (r *roundRobin) Select(nodes []*discovery.ServiceNode) *discovery.ServiceNode {
    if len(nodes) == 0 {
        return nil
    }
    node := nodes[r.index]
    r.index = (r.index + 1) % len(nodes)
    return node
}

func NewRoundRobin() LoadBalancer {
    return &roundRobin{}
}
```

#### 单元测试

**loadbalancer/round_robin_test.go**

```go
package loadbalancer

import (
    "net"
    "testing"

    "github.com/stretchr/testify/assert"
    "github.com/xialeistudio/go-service-discovery/discovery"
)

func Test_roundRobin_Select(t *testing.T) {
    a := assert.New(t)
    nodes := []*discovery.ServiceNode{
        {
            ServiceName: "test",
            IP:          net.IPv4(127, 0, 0, 1),
            Port:        8484,
            Tags:        map[string]string{},
        },
        {
            ServiceName: "test",
            IP:          net.IPv4(127, 0, 0, 2),
            Port:        8484,
            Tags:        map[string]string{},
        },
        {
            ServiceName: "test",
            IP:          net.IPv4(127, 0, 0, 3),
            Port:        8484,
            Tags:        map[string]string{},
        },
    }

    lb := NewRoundRobin()
    node := lb.Select(nodes)
    a.Equal(nodes[0], node)

    node = lb.Select(nodes)
    a.Equal(nodes[1], node)
}
```

### 加权轮询实现

加权轮询根据服务节点的权重来决定请求的分配。每个服务节点被赋予一个权重值，权重高的节点将更频繁地接收到请求。这种方法考虑了节点的不同处理能力，使得处理能力强的节点可以承担更多的流量，从而优化资源利用率并提高系统的整体性能。加权轮询适用于服务节点性能不均或有特定性能要求的场景。

**loadbalancer/weighted_round_robin.go**

```json
package loadbalancer

import (
    "sync"

    "github.com/spf13/cast"
    "github.com/xialeistudio/go-service-discovery/discovery"
)

type weightedRoundRobin struct {
    mu            sync.Mutex
    index         int
    currentWeight int
    totalWeight   int
    nodes         []*discovery.ServiceNode
}

func (w *weightedRoundRobin) Select(nodes []*discovery.ServiceNode) *discovery.ServiceNode {
    w.mu.Lock()
    defer w.mu.Unlock()

    if len(nodes) == 0 {
        return nil
    }

    // 节点变动时重新计算权重
    if !equalNodes(w.nodes, nodes) {
        w.nodes = nodes
        w.totalWeight = 0
        for _, node := range nodes {
            w.totalWeight += cast.ToInt(node.Tags["weight"])
        }
    }

    for {
        w.index = (w.index + 1) % len(nodes)
        if w.index == 0 {
            w.currentWeight -= gcd(nodes)
            if w.currentWeight <= 0 {
                w.currentWeight = w.totalWeight
                if w.currentWeight == 0 {
                    return nil
                }
            }
        }

        if cast.ToInt(nodes[w.index].Tags["weight"]) >= w.currentWeight {
            return nodes[w.index]
        }
    }
}

func equalNodes(a, b []*discovery.ServiceNode) bool {
    if len(a) != len(b) {
        return false
    }
    for i := range a {
        if a[i] != b[i] {
            return false
        }
    }
    return true
}

func gcd(nodes []*discovery.ServiceNode) int {
    gcdValue := cast.ToInt(nodes[0].Tags["weight"])
    for _, node := range nodes {
        gcdValue = gcdTwo(gcdValue, cast.ToInt(node.Tags["weight"]))
    }
    return gcdValue
}

func gcdTwo(a, b int) int {
    if b == 0 {
        return a
    }
    return gcdTwo(b, a%b)
}

func NewWeightedRoundRobin() LoadBalancer {
    return &weightedRoundRobin{}
}
```

#### 单元测试

单元测试构造节点时需要添加 weight 到节点标签。

**loadbalancer/weighted_round_robin_test.go**

```go
package loadbalancer

import (
    "net"
    "testing"

    "github.com/stretchr/testify/assert"
    "github.com/xialeistudio/go-service-discovery/discovery"
)

func Test_weightedRoundRobin_Select(t *testing.T) {
    a := assert.New(t)
    nodes := []*discovery.ServiceNode{
        {
            ServiceName: "test",
            IP:          net.IPv4(127, 0, 0, 1),
            Port:        8484,
            Tags: map[string]string{
                "weight": "90",
            },
        },
        {
            ServiceName: "test",
            IP:          net.IPv4(127, 0, 0, 2),
            Port:        8484,
            Tags: map[string]string{
                "weight": "50",
            },
        },
        {
            ServiceName: "test",
            IP:          net.IPv4(127, 0, 0, 3),
            Port:        8484,
            Tags: map[string]string{
                "weight": "80",
            },
        },
    }

    lb := NewWeightedRoundRobin()
    node := lb.Select(nodes)
    a.Equal(nodes[0], node)

    node = lb.Select(nodes)
    a.Equal(nodes[0], node)

    node = lb.Select(nodes)
    a.Equal(nodes[2], node)
}
```

### 随机实现

随机通过随机选择服务节点来处理请求。这种方法不考虑节点的负载或性能差异，而是简单地从所有可用节点中随机挑选一个来响应请求。随机策略简单易实现，适用于服务节点性能相近且无明显差异的场景，可以提供良好的负载分散，但可能不如其他策略那样精确地平衡负载。

**loadbalancer/random.go**

```go
package loadbalancer

import (
    "math/rand"
    "time"

    "github.com/xialeistudio/go-service-discovery/discovery"
)

type random struct {
    r *rand.Rand
}

func (r random) Select(nodes []*discovery.ServiceNode) *discovery.ServiceNode {
    if len(nodes) == 0 {
        return nil
    }
    index := r.r.Intn(len(nodes))
    return nodes[index]
}

func NewRandom() LoadBalancer {
    return &random{
        r: rand.New(rand.NewSource(time.Now().Unix())),
    }
}
```

r 是随机数发生器，通过 NewRandom 构造时填充了时间戳作为随机数种子，保证安全性。在单元测试时使用固定的随机数种子，保证结果的可控性。

#### 单元测试

**loadbalancer/random_test.go**

```go
package loadbalancer

import (
    "net"
    "testing"

    "github.com/stretchr/testify/assert"
    "github.com/xialeistudio/go-service-discovery/discovery"
    "math/rand"
)

func Test_random_Select(t *testing.T) {
    a := assert.New(t)
    r := rand.New(rand.NewSource(1))
    lb := random{r: r}
    nodes := []*discovery.ServiceNode{
        {
            ServiceName: "test",
            IP:          net.IPv4(127, 0, 0, 1),
            Port:        8484,
            Tags:        map[string]string{},
        },
        {
            ServiceName: "test",
            IP:          net.IPv4(127, 0, 0, 2),
            Port:        8484,
            Tags:        map[string]string{},
        },
        {
            ServiceName: "test",
            IP:          net.IPv4(127, 0, 0, 3),
            Port:        8484,
            Tags:        map[string]string{},
        },
    }

    node := lb.Select(nodes)
    a.Equal(nodes[2], node)

    node = lb.Select(nodes)
    a.Equal(nodes[0], node)

    node = lb.Select(nodes)
    a.Equal(nodes[2], node)
}
```

## 小结

在本文中，我们全面探讨了微服务架构中服务发现的设计与实现，特别关注了三种主流的服务注册中心：etcd、Consul和ZooKeeper。我们详细分析了每种技术的工作原理、特点以及它们在服务发现中的角色。

对于etcd，我们讨论了其基于Raft算法的强一致性特性，以及如何利用其丰富的客户端库来实现服务的注册与发现。Consul的章节则展示了其开箱即用的特性，包括健康检查和HTTP API接口。最后，ZooKeeper的实现部分强调了其树形结构和watch机制，这些都是构建高效服务注册中心的关键。

此外，我们还设计了一个通用的NodeRegistry接口，它定义了服务发现客户端必须实现的方法，如获取服务节点列表、注册和注销服务节点。这个接口的实现为服务发现提供了一个统一的抽象，使得服务消费者可以无缝地与不同的服务注册中心交互。

总的来说，本文为读者提供了一个关于服务发现的全面视角，包括理论基础、关键技术的深入分析以及实际的代码实现。通过学习，读者应该能够理解服务发现的重要性，掌握不同服务注册中心的使用方法，并能够根据自己的需求选择合适的技术来构建服务发现机制。