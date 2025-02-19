---
title: 服务发现的设计与实现（一）
date: 2025-02-19T11:53:08+08:00
slug: implementation-of-service-discovery-part1
categories: 
- Engineering
featured: true
tags:
- Microservices
---
服务发现是微服务架构中的一个核心组件，它允许服务实例在启动时向注册中心注册自己的元数据，如网络地址、服务名称和标签等。这些信息使得其他服务能够发现并与之通信，从而实现服务间的动态解耦和高效协作。

在本文中，我们将深入探讨服务发现的客户端接口设计。服务发现的客户端接口通常包括注册、注销和查询服务实例的方法。服务注册是服务实例将自己信息注册到注册中心的过程，注销则是服务实例在停止时从注册中心删除自己的信息。查询服务实例则是服务消费者根据服务名称查询可用的服务实例列表。

<!--more-->

我们将介绍几个知名的服务发现项目，包括etcd、Zookeeper和Consul。这些项目提供了不同的服务发现机制和客户端实现方式。例如，etcd使用Raft算法保证数据的一致性，支持服务注册与发现；Zookeeper提供了分布式协调服务，包括服务注册和健康检查；Consul则提供了全面的服务发现和健康检查功能，支持多数据中心部署。

为了将理论知识与实践相结合，本文还将提供一个简单的示例，展示如何将两个HTTP微服务与服务发现集成。我们将创建两个微服务，并通过服务发现组件实现它们的注册和发现。这个示例将帮助读者理解服务发现在实际应用中的工作方式。

## 客户端接口设计

在微服务架构中，服务发现是实现服务间通信和动态路由的关键机制。为了有效地管理和协调这些服务，我们需要设计一套健壮的客户端接口。本节将深入探讨如何构建这样的接口，包括定义服务节点（ServiceNode）、服务发现客户端（NodeRegistry）以及负载均衡器（LoadBalancer）的核心组件。我们将分析这些组件的实现原理，探讨它们在服务发现过程中的作用，以及如何通过这些接口实现服务的注册、发现和负载均衡。

**ServiceNode**

ServiceNode是服务发现机制中的一个基础组件，它代表了一个服务实例的网络位置和状态。在微服务架构中，一个服务可能由多个实例组成，每个实例都运行着相同的代码，但可能部署在不同的物理或虚拟机器上。ServiceNode 结构体通常包含服务实例的 IP 地址、端口号以及一系列标签（tags），这些标签可以用于进一步描述服务实例的特性，如版本号、环境（开发、测试、生产）等。

```go
type ServiceNode struct {
  ServiceName string
  IP    net.IP
  Port   int
  Tags   map[string]string
}
```

这样的设计允许服务消费者根据标签选择特定的服务实例进行调用，例如，可能只想调用某个特定版本的服务实例，或者基于标签进行路由选择。

**NodeRegistry**

DiscoveryClient 是服务发现机制的核心接口，它定义了服务发现客户端必须实现的方法。这些方法包括获取服务节点列表、注册当前节点到服务注册中心以及注销节点。NodeRegistry接口的实现负责与服务注册中心的交互，无论是通过 REST API、gRPC 还是其他通信协议。

```go
type NodeRegistry interface {
  GetNodes(ctx context.Context, serverName string, tags map[string]string) ([]*ServiceNode, error)
  Register(ctx context.Context, node *ServiceNode) error
  Unregister(ctx context.Context, node *ServiceNode) error

}
```

这种接口设计使得服务发现客户端可以与具体的服务注册中心实现解耦，提高了代码的可维护性和可扩展性。服务消费者可以通过实现此接口的任何客户端库与不同的服务注册中心进行交互，而无需关心背后的实现细节。

**LoadBalancer**

LoadBalancer 定义了负载均衡器的接口，它负责从服务发现客户端获取的服务节点列表中选择一个节点来处理请求。负载均衡器可以采用不同的策略，如轮询、随机选择、加权轮询或基于 IP 哈希的策略，以确保请求均匀地分配到各个服务实例。

```go
type LoadBalancer interface {
  Select(nodes []*ServiceNode) *ServiceNode
}
```

负载均衡器的设计对于提高系统的可用性和响应性至关重要。通过实现不同的负载均衡策略，可以为不同的业务场景提供最适合的请求分配机制。

**DiscoveryClient**

对于业务应用来说，只需要根据服务名称获取一个节点信息然后进行请求即可。因此应该组合NodeRegistry和LoadBalancer的能力，获取到节点列表后直接进行路由，最后将最终节点返回给业务应用。

```go
type DiscoveryClient struct {
 LoadBalancer LoadBalancer
 Registry NodeRegistry
}
func (d *DiscoveryClient) Resolve(ctx context.Context, serviceName)(*ServiceNode) {
 // TODO 返回服务节点
}
```

## etcd

etcd(https://etcd.io/)是一个高度一致的分布式键值存储，它提供了一种可靠的方式来存储需要由分布式系统或机器集群访问的数据。它在微服务和 Kubernetes 集群中不仅可以作为服务注册于发现，还可以作为 key-value 存储的中间件。etcd 的目标是构建一个高可用的分布式键值数据库，具有简单、键值对存储、监测变更、安全、快速和可靠等特点。它采用 Raft 算法实现分布式系统数据的高可用性、一致性，并且使用 Go 语言编写，具有出色的跨平台支持和强大的社区。

etcd 的架构包括 client 层、API 网络层、Raft 算法层和存储层。client 层包含 client v2 和 v3 两个版本的 API 客户端。API 网络层处理客户端访问服务器和服务器节点间的通信协议。Raft 算法层实现了 Leader 选举、日志复制等核心算法特性，保障 etcd 多节点间的数据一致性。存储层包含预写日志 WAL 模块、快照 Snapshot 模块和 boltdb 模块，其中 WAL 可保障 etcd crash 后数据不丢失，boltdb 则保存了集群元数据和用户写入的数据。

etcd 的应用场景广泛，最常用于服务注册与发现，作为集群管理的组件使用，也可以作为 K-V 存储，作为数据库使用。它的存储特点是采用 kv 型数据存储，支持动态存储和静态存储，分布式存储，可集成为多节点集群，存储方式采用类似目录结构。

在安全性方面，etcd 支持通过 TLS 协议进行的加密通信，包括对等体之间的加密内部群集通信以及加密的客户端流量。通过使用 SSL 证书，etcd 可以实现互联网的通信安全，防止窃听、篡改和冒充风险。

本节我们基于etcd来实现前文中设计的接口。

**etcd的安装与启动**

要开始使用 etcd，您可以访问 GitHub 上的 etcd 仓库，具体网址为 https://github.com/etcd-io/etcd/releases/，从中下载与您的操作系统相匹配的二进制文件。下载完成后，您可以通过执行 etcd 的二进制文件来启动一个单节点的 etcd 服务器。在本节中，我们将重点介绍如何利用 etcd 实现服务发现客户端，因此，对于演示目的而言，单节点的 etcd 服务器已经足够。但请注意，在生产环境中，为了确保高可用性和数据一致性，强烈推荐使用 etcd 的集群部署。

为了验证您的 etcd 服务器是否已经正常运行，您可以使用 etcdctl 这个命令行工具来进行测试。首先，打开一个新的终端窗口，然后输入 `etcdctl put greeting "Hello, etcd"` 命令，如果一切正常，您应该会看到 "OK" 作为返回结果。接下来，通过执行 `etcdctl get greeting` 命令，您应该能够看到预期的输出 "Hello, etcd"。这表明您的 etcd 服务器已经成功启动，并且可以正常处理键值存储的读写操作。

**包结构设计**

作为我们的首个服务注册中心实现，在开始编码之前，让我们先规划一下包结构的设计。这将帮助我们组织代码，确保项目的可维护性和可扩展性。以下是我们为etcd服务注册中心设计的包结构概览：

```
├── client
│  └── client.go
├── discovery
│  ├── discovery.go
│  └── etcd
│    ├── registry.go
│    └── registry_test.go
├── go.mod
└── loadbalancer
└── loadbalancer.go
```
+ client: 服务注册客户端，提供给应用层使用
+ discovery: 服务注册接口声明
	+ etcd: 服务注册的etcd实现
+ loadbalancer: 负载均衡接口声明

**编写接口**

根据之前的设计，我们直接在discovery/discovery.go编写服务节点和注册中心的声明。

在工程实践中，注册中心会本地缓存服务的实例列表，避免频繁请求注册中心导致注册中心过载影响服务发现。下列代码使用的sync.Map来保证并发安全。

discovery/discovery.go

```go
package discovery

import (
  "context"
  "net"
)

// ServiceNode 服务节点
type ServiceNode struct {
  ServiceName string
  IP     net.IP
  Port    int
  Tags    map[string]string
}

// NodeRegistry 服务节点注册中心
type NodeRegistry interface {
  // GetNodes 获取服务节点
  GetNodes(ctx context.Context, serviceName string, tags map[string]string) ([]*ServiceNode, error)
  // Register 注册服务节点
  Register(ctx context.Context, node *ServiceNode) error
  // Unregister 注销服务节点
  Unregister(ctx context.Context, node *ServiceNode) error
}

// MatchTags 匹配标签
func MatchTags(nodeTags, queryTags map[string]string) bool {
  for name, value := range queryTags {
    if nodeTags[name] != value {
      return false
    }
  }
  return true
}
```



**编写实现**

实现类的流程基本是类似的，在GetNodes方法中优先读取本地缓存，如果不存在，则远程请求注册中心，并监听节点变更事件，实现本地节点的实时变更。在Register方法中注册节点并实现心跳机制，在etcd中，心跳机制是基于租约实现的，只要定期续约，节点就会存活。

discovery/etcd/registry.go
```go
package etcd

import (
  "context"
  "fmt"
  json "github.com/json-iterator/go"
  "github.com/xialeistudio/go-service-discovery/discovery"
  "go.etcd.io/etcd/client/v3"
  "log"
  "strconv"
  "sync"
  "time"
)

var (
  // DialTimeout 默认的连接超时时间
  DialTimeout = 5 * time.Second
  // LeaseTTL 默认的租约时间
  LeaseTTL = 10 * time.Second
)

type registry struct {
  nodeListMap *sync.Map // <serviceName, <nodeKey, *ServiceNode>>
  client *clientv3.Client
  watcher clientv3.Watcher
  kv   clientv3.KV
}

func NewRegistry(endpoints []string) (discovery.NodeRegistry, error) {
  config := clientv3.Config{
    Endpoints:  endpoints,
    DialTimeout: DialTimeout,
  }
  client, err := clientv3.New(config)
  if err != nil {
    return nil, fmt.Errorf("failed to create etcd client: %v", err)

  }
  return &registry{
    nodeListMap: &sync.Map{},
    client:   client,
    kv:     clientv3.NewKV(client),
    watcher:   clientv3.NewWatcher(client),
  }, nil
}

func (r *registry) GetNodes(ctx context.Context, serviceName string, tags map[string]string) ([]*discovery.ServiceNode, error) {
  // 检查本地缓存是否有服务节点
  nodes, exists := r.nodeListMap.Load(serviceName)
  if !exists {
    var err error
    // 本地缓存为空，从 etcd 拉取
    nodes, err = r.pullNodes(ctx, serviceName)
    if err != nil {
      return nil, err
    }
    // 缓存到本地
    r.nodeListMap.Store(serviceName, nodes)
    // 启动协程监听节点变化
    go r.watchNodes(ctx, serviceName)
  }

  // 根据标签过滤服务节点
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
  value, err := json.MarshalToString(node)
  if err != nil {
    return fmt.Errorf("failed to marshal service node: %v", err)
  }
  // 创建租约
  lease, err := r.client.Grant(ctx, int64(LeaseTTL.Seconds()))
  if err != nil {
    return err
  }
// 将服务节点信息写入etcd
  key := makeNodeKey(node)
  _, err = r.kv.Put(ctx, key, value, clientv3.WithLease(lease.ID))
  if err != nil {
    return fmt.Errorf("failed to put key to etcd: %v", err)
  }
  // 续租
  go r.keepLeaseAlive(lease.ID, node)
  return nil
}

func (r *registry) Unregister(ctx context.Context, node *discovery.ServiceNode) error {
  key := makeNodeKey(node)
  _, err := r.kv.Delete(ctx, key)
  if err != nil {
    return fmt.Errorf("failed to delete key from etcd: %v", err)
  }
  r.removeNode(node)
  return nil
}

func makeNodeKey(node *discovery.ServiceNode) string {
  return node.ServiceName + "/" + node.IP.String() + ":" + strconv.Itoa(node.Port)
}

// 续租
func (r *registry) keepLeaseAlive(leaseId clientv3.LeaseID, node *discovery.ServiceNode) {
  ticker := time.NewTicker(LeaseTTL / 2)
  defer ticker.Stop()
  for range ticker.C {
    func() {
      _, err := r.client.KeepAliveOnce(context.Background(), leaseId)
      if err != nil {
       r.removeNode(node)
       return
      }
    }()
  }
}

func (r *registry) removeNode(node *discovery.ServiceNode) {
  r.nodeListMap.Range(func(key, value interface{}) bool {
​    nodes := value.(*sync.Map)
​    nodes.Delete(makeNodeKey(node))
​    return true
  })
}

func (r *registry) pullNodes(ctx context.Context, serviceName string) (*sync.Map, error) {
  resp, err := r.kv.Get(ctx, serviceName+"/", clientv3.WithPrefix())
  if err != nil {
​    return nil, fmt.Errorf("failed to get nodeListMap from etcd: %v", err)
  }
  var nodes sync.Map
  for _, kv := range resp.Kvs {
​    node := &discovery.ServiceNode{}
​    if err := json.Unmarshal(kv.Value, node); err != nil {
​      return nil, fmt.Errorf("failed to unmarshal node data: %v", err)
​    }
​    nodes.Store(string(kv.Key), node)
  }
  return &nodes, nil
}

 

func (r *registry) watchNodes(ctx context.Context, serviceName string) {
  watchChan := r.watcher.Watch(ctx, serviceName+"/", clientv3.WithPrefix())
  for wResp := range watchChan {
​    for _, ev := range wResp.Events {
​      switch ev.Type {
​      case clientv3.EventTypePut:
​       // 新增或更新服务节点
​       node := &discovery.ServiceNode{}
​       if err := json.Unmarshal(ev.Kv.Value, node); err != nil {
​         log.Printf("failed to unmarshal node data: %v", err)
​         continue
​       }
​       r.nodeListMap.LoadOrStore(serviceName, &sync.Map{})
​       nodes, _ := r.nodeListMap.Load(serviceName)
​       nodes.(*sync.Map).Store(string(ev.Kv.Key), node)
​      case clientv3.EventTypeDelete:
​       // 删除服务节点
​       nodes, _ := r.nodeListMap.Load(serviceName)
​       nodes.(*sync.Map).Delete(string(ev.Kv.Key))
​      }
​    }
  }
}
```
registry结构体实现了 discovery.NodeRegistry 接口，用于管理微服务架构中的服务节点。结构体包含一个节点映射 nodes，用于缓存服务节点信息，以及 etcd 客户端 client，用于与 etcd 集群通信。

NewRegistry 函数用于初始化 etcd 客户端并创建 registry 实例。它接受 etcd 服务端点列表作为参数，并配置客户端以连接到 etcd 集群。

GetNodes 方法用于获取指定服务名称的服务节点列表。如果本地缓存中不存在该服务的节点信息，它会从 etcd 中拉取节点信息，并启动一个协程 watchNodes 来监听 etcd 中服务节点的变化。

Register 方法允许服务节点将自己注册到 etcd 中，并创建一个租约以保持其注册信息的有效性。它还启动一个协程 keepLeaseAlive 来续租，确保节点信息不会过期。

Unregister 方法用于从 etcd 中注销服务节点，并更新本地缓存。

keepLeaseAlive 方法负责定期续租，以保持服务节点在 etcd 中的注册信息不过期。

removeNode 方法用于从本地缓存中移除已注销的服务节点。

pullNodes 方法从 etcd 中拉取服务节点信息，并将其反序列化为 ServiceNode 对象列表。

watchNodes 方法监听 etcd 中服务节点的变化事件，并更新本地缓存。

**单元测试编写**

在微服务架构中，服务注册中心的稳定性和可靠性对于整个系统的运行至关重要。为了确保我们的 etcd 服务注册中心能够正确地处理服务节点的注册、查询和注销操作，我们编写了一系列单元测试来验证其功能。这些测试不仅涵盖了单个服务节点的注册和注销，还包括了多节点多标签的场景，确保服务发现逻辑在各种情况下都能正常工作。

discovery/etcd/registry_test.go

```go
package etcd

import (
  "context"
  "github.com/stretchr/testify/assert"
  "go-service-discovery/discovery"
  "net"
  "testing"
  "time"
)

func TestEtcdRegistry(t *testing.T) {
  a := assert.New(t)
  r, err := NewRegistry([]string{"localhost:2379"})
  a.Nil(err)
  t.Run("Register single node", func(t *testing.T) {
​    node := &discovery.ServiceNode{
​      ServiceName: "test",
​      IP:     net.IPv4(127, 0, 0, 1),
​      Port:    8484,
​      Tags: map[string]string{
​       "version": "1.0",
​      },
​    }
​    // 注册节点
​    err = r.Register(context.Background(), node)
​    a.Nil(err)
​    time.Sleep(time.Millisecond * 100)
​    // 获取节点
​    nodes, err := r.GetNodes(context.Background(), "test", map[string]string{
​      "version": "1.0",
​    })
​    a.Nil(err)
​    a.Len(nodes, 1)
​    a.Equal(node, nodes[0])
​    // 注销节点
​    err = r.Unregister(context.Background(), node)
​    a.Nil(err)

​    time.Sleep(time.Millisecond * 100)
​    // 获取节点
​    nodes, err = r.GetNodes(context.Background(), "test", map[string]string{
​      "version": "1.0",
​    })
​    a.Nil(err)
​    a.Len(nodes, 0)
  })
  t.Run("Register multi nodes with multi tags", func(t *testing.T) {
​    node1 := &discovery.ServiceNode{
​      ServiceName: "test",
​      IP:     net.IPv4(127, 0, 0, 1),
​      Port:    8484,
​      Tags: map[string]string{
​       "version": "1.0",
​       "region": "cn",
​      },
​    }
​    node2 := &discovery.ServiceNode{
​      ServiceName: "test",
​      IP:     net.IPv4(127, 0, 0, 2),
​      Port:    8484,
​      Tags: map[string]string{
​       "version": "1.0",
​       "region": "us",
​      },
​    }
​    // 注册节点
​    err = r.Register(context.Background(), node1)
​    a.Nil(err)
​    err = r.Register(context.Background(), node2)
​    a.Nil(err)
​    time.Sleep(time.Millisecond * 100)
​    // 获取节点
​    nodes, err := r.GetNodes(context.Background(), "test", map[string]string{
​      "version": "1.0",
​      "region": "cn",
​    })
​    a.Nil(err)
​    a.Len(nodes, 1)
​    a.Equal(node1, nodes[0])
​    // 获取节点
​    nodes, err = r.GetNodes(context.Background(), "test", map[string]string{
​      "version": "1.0",
​      "region": "us",
​    })
​    a.Nil(err)
​    a.Len(nodes, 1)
​    a.Equal(node2, nodes[0])
​    // 获取节点
​    nodes, err = r.GetNodes(context.Background(), "test", nil)
​    a.Nil(err)
​    a.Len(nodes, 2)
​    // 注销节点
​    err = r.Unregister(context.Background(), node1)
​    a.Nil(err)
​    err = r.Unregister(context.Background(), node2)
​    a.Nil(err)
​    time.Sleep(time.Millisecond * 100)
​    // 获取节点
​    nodes, err = r.GetNodes(context.Background(), "test", map[string]string{
​      "version": "1.0",
​    })
​    a.Nil(err)
​    a.Len(nodes, 0)
  })
}
```
需要说明的是，测试代码中包含了time.Sleep操作来阻塞协程，这是因为节点监听是在另外的协程实现的，是异步过程，需要阻塞主协程来让异步代码执行完毕，更新本地节点缓存后才能通过测试。

本节详细介绍了基于 etcd 的服务注册中心实现，涵盖了从客户端初始化、服务节点的注册与注销，到服务节点的查询和监听等功能。通过 etcd 强大的分布式键值存储能力，我们构建了一个高可用和一致性的服务发现机制。测试部分验证了服务注册中心在处理单节点和多节点场景下的正确性和稳定性，确保了服务发现过程中数据的准确性和实时性通过本节的学习，我们不仅理解了 etcd 在服务发现中的关键作用，还掌握了如何在实际项目中应用 etcd 来实现服务注册与发现。



后面会继续更新基于Consul和zookeeper的服务发现和注册中心的实现。