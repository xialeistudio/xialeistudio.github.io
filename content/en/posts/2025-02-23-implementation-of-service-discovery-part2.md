---
title: Designing and Implementing Service Discovery (Part 2)
date: 2025-02-23T11:53:08+08:00
slug: implementation-of-service-discovery-part2
categories:
- architecture
tags:
- Microservices
series:
- microservices
---

In a microservices architecture, service discovery is the mechanism that keeps inter-service communication efficient and lets the system scale dynamically. As distributed systems grow more complex, designing a reliable, high-performance service discovery solution has become a core engineering concern.

This is the second part of the "Designing and Implementing Service Discovery" series, and it digs into concrete service registry implementations and load balancing strategies. We focus on three mainstream technologies, etcd, Consul, and ZooKeeper, look at how they work and where they fit, and build service discovery with real code. We also cover common load balancing algorithms and how to implement them, to show how request distribution can be optimized in microservices. 
<!--more-->

## Consul Registry

Consul is an open-source service mesh solution that provides service discovery, configuration, and segmentation. It combines several key building blocks of distributed systems: service discovery, health checking, a key-value store, and multi-datacenter support. Its design goal is to offer a simple, flexible, and reliable way to build and run distributed systems.

At Consul's core is a distributed service catalog: service instances register themselves along with their metadata, and other services discover them by querying the catalog. Health checks ensure that clients only discover healthy instances. Consul also ships with built-in DNS and HTTP API interfaces for service discovery, which keeps communication between services simple.

Consul also supports distributed, consistent configuration, so teams can store and synchronize configuration data. Its segmentation feature isolates services across different network environments, which is very useful for blue-green deployments and canary releases in a microservices architecture.

Consul is built for high availability. It uses the Raft algorithm to guarantee data consistency and fault tolerance, and is usually deployed as a cluster in which every node takes part in replication and consistency. This design makes Consul a strong tool for building modern cloud-native applications, especially when service discovery and configuration management have to span multiple datacenters or cloud environments.

### Installing and Starting Consul

To use Consul as a service registry, first install it. Download the Consul binary for your operating system from the official HashiCorp developer site: [https://developer.hashicorp.com/consul/install](https://developer.hashicorp.com/consul/install).

Once installed, open a terminal and run the following command to start Consul in development server mode. This starts a single-node Consul server, suitable for development and testing.

```bash
consul agent -dev -bind 127.0.0.1
```

Next, in a new terminal session, set a key-value pair with the command below. It stores a simple string value and returns the result of the operation. If it succeeds, you should see "true" as the output.

```bash
curl \
  --request PUT \
  --data 'hello consul' \
  http://127.0.0.1:8500/v1/kv/foo
```

Finally, to verify that the key-value pair was set correctly, retrieve the key's value with the following command. The output shows the key "foo" and its value, encoded in Base64.

```
curl http://127.0.0.1:8500/v1/kv/foo
```

The expected output looks like this, showing the details of key "foo", including its value "aGVsbG8gY29uc3Vs" (the Base64 encoding of "hello consul"):

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

### Package Structure

We simply add a consul package on top of the structure from the previous part.

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

### Implementation

The Consul service discovery client follows the same logic as the etcd one: get nodes, register a service instance, and deregister a service instance. The differences are that Consul's watch mechanism works differently from etcd's, and Consul supports health checks.

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
        // Local cache is empty, pull from consul
        nodes, err = r.pullNodes(ctx, serviceName)
        if err != nil {
            return nil, err
        }
        // Cache locally
        r.nodeListMap.Store(serviceName, nodes)
        // Start watching
        go r.watchNodes(serviceName)
    }
    // Filter nodes by tags
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
        Check: &capi.AgentServiceCheck{ // Health check
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

The watch mechanism lets clients listen for service state changes in real time. In the code above, watchNodes watches the service in Consul; whenever an instance registers or deregisters, the handler updates the local cache so that consumers always see the latest list of service nodes. This lets consumers react promptly to changes in providers, making the system more dynamic and reliable.

Health checks ensure that only healthy instances are visible to consumers; the code above uses a TCP connection check. As soon as an instance has a problem, Consul automatically marks it unhealthy and removes it from service discovery, so no traffic is routed to it.

### Unit Tests

Because the registry is designed against an interface, etcd and Consul are just two implementations, and the unit tests can be shared. The only difference is the code that initializes the registry.

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
    // Initialize the registry
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
        // Register the node
        err = r.Register(context.Background(), node)
        a.Nil(err)
        time.Sleep(time.Millisecond * 100)
        // Get nodes
        nodes, err := r.GetNodes(context.Background(), "test", map[string]string{
            "version": "1.0",
        })
        a.Nil(err)
        a.Len(nodes, 1)
        a.Equal(node, nodes[0])
        // Deregister the node
        err = r.Unregister(context.Background(), node)
        a.Nil(err)
        time.Sleep(time.Millisecond * 100)
        // Get nodes
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
        // Register the nodes
        err = r.Register(context.Background(), node1)
        a.Nil(err)
        err = r.Register(context.Background(), node2)
        a.Nil(err)
        time.Sleep(time.Millisecond * 100)
        // Get nodes
        nodes, err := r.GetNodes(context.Background(), "test", map[string]string{
            "version": "1.0",
            "region":  "cn",
        })
        a.Nil(err)
        a.Len(nodes, 1)
        str, _ := json.MarshalToString(nodes)
        t.Log(str)
        a.Equal(node1, nodes[0])
        // Get nodes
        nodes, err = r.GetNodes(context.Background(), "test", map[string]string{
            "version": "1.0",
            "region":  "us",
        })
        a.Nil(err)
        a.Len(nodes, 1)
        a.Equal(node2, nodes[0])
        // Get nodes
        nodes, err = r.GetNodes(context.Background(), "test", nil)
        a.Nil(err)
        a.Len(nodes, 2)
        // Deregister the nodes
        err = r.Unregister(context.Background(), node1)
        a.Nil(err)
        err = r.Unregister(context.Background(), node2)
        a.Nil(err)
        time.Sleep(time.Millisecond * 100)
        // Get nodes
        nodes, err = r.GetNodes(context.Background(), "test", map[string]string{
            "version": "1.0",
        })
        a.Nil(err)
        a.Len(nodes, 0)
    })
}
```

Make sure the Consul server is running, then run the tests.

As a service registration and discovery tool, Consul plays a vital role in a microservices architecture. It provides a centralized service registry through which service instances can find and talk to each other. During registration, each instance registers itself with Consul along with a health check that verifies its availability. Consul's watch mechanism lets consumers listen for service state changes in real time and update their local node lists accordingly. This dynamic service discovery makes the system more flexible and scalable and further decouples services. Together, these features keep a microservices architecture running efficiently and stably, making Consul an ideal choice for modern cloud-native applications.

## ZooKeeper Registry

ZooKeeper is a distributed coordination service that provides consistent coordination for distributed applications. As an open-source coordination service, it offers a set of primitives that developers can use to build reliable distributed synchronization.

At the heart of ZooKeeper is its state machine model: it maintains a hierarchical namespace, similar to a file system tree. Each node in this namespace is called a znode and can store data and state information. Clients implement service registration and discovery by creating, reading, updating, and deleting znodes.

In microservices, ZooKeeper is often used as a service registry. On startup, a service instance registers its information, such as its IP address and port, in ZooKeeper, and other services discover available providers by querying these znodes. ZooKeeper also provides a watch mechanism that lets instances listen for znode changes, enabling dynamic service discovery and load balancing.

### Installing and Starting ZooKeeper

ZooKeeper is a Java-based distributed coordination service, so it needs a Java runtime. First make sure a JDK or JRE is installed on your system. You can download the Java version for your operating system from [https://www.java.com/zh-CN/download/help/download_options_zh-cn.html](https://www.java.com/zh-CN/download/help/download_options_zh-cn.html) and install it.

Once installed, open a terminal or command prompt and run the following command to verify that Java is installed:

```bash
java -version
```

For example, here is the output on my system:

```
openjdk version "17.0.9" 2023-10-17
OpenJDK Runtime Environment Homebrew (build 17.0.9+0)
OpenJDK 64-Bit Server VM Homebrew (build 17.0.9+0, mixed mode, sharing)
```

Next, download the latest ZooKeeper release from https://zookeeper.apache.org/releases.html, then extract and configure it following the provided guide.

To start the ZooKeeper service, run the following command in a terminal. It runs ZooKeeper in the foreground, so you can watch its output in real time:

```bash
zkServer start-foreground
```

To connect to the ZooKeeper server, run the following command in a new terminal session:

```bash
zkCli
```

Once connected, run `stat /` to inspect the root node's status. Here is my sample output:

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

At this point ZooKeeper is installed and running, and we can interact with it from the command line.

### Implementation

In ZooKeeper, a parent path must exist before child nodes can be added under it. So we first create the root path /services, then make sure the service name node exists before registering, and finally create the service instance node.

Our watch implementation fetches the node details after each node event. If a node's data cannot be fetched, the node has been deleted, and we must skip it and continue the loop rather than return; otherwise the local cache would never be updated.

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
    // DialTimeout is the default connection timeout
    DialTimeout = 5 * time.Second
    // BasePath is the root path for service registration
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
        // Local cache is empty, pull from zookeeper
        nodes, err = r.pullNodes(ctx, serviceName)
        if err != nil {
            return nil, err
        }
        // Cache locally
        r.nodeListMap.Store(serviceName, nodes)
        // Start watching
        go r.watchNodes(serviceName)
    }
    // Filter nodes by tags
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
            if err != nil { // If the event was triggered by a node deregistering, its data can't be fetched here; just skip it instead of failing, otherwise the local nodes can't be updated
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

In ZooKeeper, ephemeral nodes can only be created under persistent nodes, so the service name node is persistent while service instance nodes are ephemeral. When the connection between a registered instance and the ZooKeeper server drops, its ephemeral node is deleted automatically.

### Unit Tests

The unit tests are the same as for etcd and Consul; only the registry initialization differs:

**discovery/zookeeper/registry_test.go**

```go
r, err := NewRegistry([]string{"localhost:2181"})
a.Nil(err)
```

ZooKeeper is a high-performance distributed coordination service that provides key coordination capabilities for building large distributed systems. As a service registry, it stores service instance information and lets consumers query and subscribe to it. Its tree structure makes registration and discovery intuitive and flexible, and its ephemeral nodes and watch mechanism further strengthen the registry by enabling dynamic management and automatic updates of service instances. These features make ZooKeeper an ideal choice for service discovery and coordination in microservices, especially where strong consistency and high reliability are required.

## Load Balancing

In a microservices architecture, load balancing of service calls is critical: it determines how a large volume of requests is distributed across multiple service instances. A good load balancing strategy can significantly improve throughput, response times, and overall reliability. This section explains how load balancing works and how to implement it, covering several common algorithms, including round robin, random, and weighted round robin, along with where each fits and how it is implemented.

### How It Works

At its core, load balancing selects one node from a group of service nodes to handle a client request. An algorithm decides which node receives a given request, with the goal of keeping load across nodes as even as possible to improve overall performance and reliability. The load balancer distributes requests according to a predefined strategy, such as round robin, random selection, or least connections, so that no single node becomes overloaded and destabilizes the service.

### Round Robin

The round robin strategy cycles through the list of service nodes, assigning each new request to the next available instance in turn. This sequential approach is simple and fair: over time every node receives roughly the same number of requests, which balances load effectively and improves resource utilization. Round robin is especially suitable when all service nodes have similar performance.

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

#### Unit Tests

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

### Weighted Round Robin

Weighted round robin distributes requests according to node weights. Each service node is assigned a weight, and nodes with higher weights receive requests more often. This accounts for differences in processing capacity, letting more powerful nodes take more traffic, which improves resource utilization and overall performance. Weighted round robin suits scenarios where node performance is uneven or there are specific performance requirements.

**loadbalancer/weighted_round_robin.go**

```go
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

    // Recalculate weights when the node list changes
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

#### Unit Tests

When constructing nodes in the tests, add a weight to each node's tags.

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

### Random

The random strategy handles each request by picking a service node at random. It ignores differences in node load or performance and simply chooses one of the available nodes to serve the request. Random selection is simple to implement and suits scenarios where nodes have similar performance with no significant differences. It spreads load well, but may not balance it as precisely as other strategies.

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

r is the random number generator. NewRandom seeds it with the current timestamp to ensure security. The unit test uses a fixed seed so that results are deterministic.

#### Unit Tests

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

## Summary

In this article, we took a comprehensive look at the design and implementation of service discovery in a microservices architecture, focusing on three mainstream service registries: etcd, Consul, and ZooKeeper. We examined how each one works, its characteristics, and its role in service discovery.

For etcd, we discussed its strong consistency based on the Raft algorithm and how to use its rich client libraries to implement service registration and discovery. The Consul section showed its out-of-the-box features, including health checks and the HTTP API. Finally, the ZooKeeper implementation highlighted its tree structure and watch mechanism, both key to building an efficient service registry.

We also designed a generic NodeRegistry interface that defines the methods a service discovery client must implement, such as listing service nodes and registering and deregistering them. This interface provides a unified abstraction for service discovery, so consumers can work seamlessly with different service registries.

Overall, this article offers a complete view of service discovery, from theoretical foundations and in-depth analysis of key technologies to working code. After reading it, you should understand why service discovery matters, know how to use different service registries, and be able to choose the right technology to build service discovery for your own needs.
