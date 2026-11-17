---
title: Designing and Implementing Service Discovery (Part 1)
date: 2025-02-19T11:53:08+08:00
slug: implementation-of-service-discovery-part1
categories:
- architecture
featured: true
tags:
- Microservices
series:
- microservices
---
Service discovery is a core component of a microservices architecture. When a service instance starts, it registers its metadata, such as network address, service name, and tags, with a registry. Other services use this information to find and communicate with it, which keeps services dynamically decoupled and lets them work together efficiently.

In this article, we take a close look at the design of the service discovery client interface. Such an interface usually provides methods to register, deregister, and query service instances. Registration is how an instance publishes its information to the registry; deregistration removes that information when the instance stops; and querying lets a service consumer look up the list of available instances by service name.

<!--more-->

We will introduce several well-known service discovery projects: etcd, Zookeeper, and Consul. Each offers a different discovery mechanism and client implementation. For example, etcd uses the Raft algorithm to guarantee data consistency and supports service registration and discovery; Zookeeper provides distributed coordination, including service registration and health checks; and Consul offers comprehensive service discovery and health checking, with support for multi-datacenter deployments.

To connect theory with practice, this article also walks through a simple example of integrating two HTTP microservices with service discovery. We will create two microservices and have them register and discover each other through a service discovery component. The example shows how service discovery works in a real application.

## Client Interface Design

In a microservices architecture, service discovery is the key mechanism behind inter-service communication and dynamic routing. To manage and coordinate these services effectively, we need a robust set of client interfaces. This section explains how to build them, defining the core components: the service node (ServiceNode), the service discovery client (NodeRegistry), and the load balancer (LoadBalancer). We will look at how these components work, what role each plays in service discovery, and how together they handle service registration, discovery, and load balancing.

**ServiceNode**

ServiceNode is a basic building block of service discovery. It represents the network location and state of a single service instance. In a microservices architecture, a service may consist of multiple instances that run the same code but are deployed on different physical or virtual machines. The ServiceNode struct typically holds the instance's IP address, port, and a set of tags that further describe the instance, such as its version or environment (development, testing, production).

```go
type ServiceNode struct {
  ServiceName string
  IP    net.IP
  Port   int
  Tags   map[string]string
}
```

This design lets service consumers pick specific instances by tag, for example to call only instances of a particular version, or to make routing decisions based on tags.

**NodeRegistry**

NodeRegistry is the core interface of service discovery. It defines the methods a discovery client must implement: fetching the list of service nodes, registering the current node with the registry, and deregistering a node. An implementation of NodeRegistry handles all interaction with the registry, whether over a REST API, gRPC, or another protocol.

```go
type NodeRegistry interface {
  GetNodes(ctx context.Context, serverName string, tags map[string]string) ([]*ServiceNode, error)
  Register(ctx context.Context, node *ServiceNode) error
  Unregister(ctx context.Context, node *ServiceNode) error

}
```

This interface decouples the discovery client from any specific registry implementation, which improves maintainability and extensibility. Service consumers can talk to different registries through any client library that implements this interface, without caring about the details behind it.

**LoadBalancer**

LoadBalancer defines the load balancer interface. It picks one node from the list returned by the discovery client to handle a request. A load balancer can use different strategies, such as round robin, random, weighted round robin, or IP hash, to spread requests evenly across service instances.

```go
type LoadBalancer interface {
  Select(nodes []*ServiceNode) *ServiceNode
}
```

Load balancer design is critical to a system's availability and responsiveness. By implementing different strategies, we can give each business scenario the request distribution that suits it best.

**DiscoveryClient**

A business application only needs to get one node for a given service name and send its request there. So we combine NodeRegistry and LoadBalancer: fetch the node list, route right away, and return the selected node to the application.

```go
type DiscoveryClient struct {
 LoadBalancer LoadBalancer
 Registry NodeRegistry
}
func (d *DiscoveryClient) Resolve(ctx context.Context, serviceName)(*ServiceNode) {
 // TODO return a service node
}
```

## etcd

etcd (https://etcd.io/) is a strongly consistent, distributed key-value store that provides a reliable way to store data that needs to be accessed by a distributed system or a cluster of machines. In microservices and Kubernetes clusters, it serves not only for service registration and discovery but also as key-value storage middleware. etcd aims to be a highly available distributed key-value database that is simple, supports key-value storage and change watching, and is secure, fast, and reliable. It uses the Raft algorithm to keep data highly available and consistent across a distributed system, and it is written in Go, with excellent cross-platform support and a strong community.

The etcd architecture consists of a client layer, an API network layer, a Raft algorithm layer, and a storage layer. The client layer includes both the v2 and v3 API clients. The API network layer handles the protocols for client-to-server and server-to-server communication. The Raft layer implements core features such as leader election and log replication, which keep data consistent across etcd nodes. The storage layer includes the write-ahead log (WAL) module, the snapshot module, and the boltdb module: WAL ensures no data is lost if etcd crashes, and boltdb stores cluster metadata and user data.

etcd has a wide range of use cases. It is most commonly used for service registration and discovery as a cluster management component, and it can also serve as a K-V store or database. It stores data as key-value pairs, supports both dynamic and static storage as well as distributed storage, can run as a multi-node cluster, and organizes keys in a directory-like structure.

On the security side, etcd supports encrypted communication over TLS, covering both internal cluster traffic between peers and client traffic. With SSL certificates, etcd can communicate securely over the internet, guarding against eavesdropping, tampering, and impersonation.

In this section, we implement the interfaces designed above on top of etcd.

**Installing and Starting etcd**

To get started with etcd, visit the etcd repository on GitHub at https://github.com/etcd-io/etcd/releases/ and download the binary for your operating system. Once downloaded, run the etcd binary to start a single-node etcd server. Since this section focuses on implementing a service discovery client with etcd, a single-node server is enough for demonstration. In production, however, a clustered etcd deployment is strongly recommended to ensure high availability and data consistency.

To verify that your etcd server is running, test it with the etcdctl command-line tool. Open a new terminal and run `etcdctl put greeting "Hello, etcd"`. If everything works, you should see "OK". Then run `etcdctl get greeting`, and you should see the expected output "Hello, etcd". This confirms that the etcd server is up and handling key-value reads and writes correctly.

**Package Layout**

Since this is our first registry implementation, let's plan the package layout before writing any code. This keeps the code organized and the project maintainable and extensible. Here is an overview of the package layout for the etcd registry:

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
+ client: the service registration client, used by the application layer
+ discovery: service registration interface declarations
	+ etcd: the etcd implementation of service registration
+ loadbalancer: load balancer interface declarations

**Writing the Interfaces**

Following the earlier design, we write the declarations for the service node and the registry directly in discovery/discovery.go.

In practice, a registry client caches the service instance list locally, so it does not overload the registry with frequent requests and disrupt service discovery. The code below uses sync.Map for concurrency safety.

discovery/discovery.go

```go
package discovery

import (
  "context"
  "net"
)

// ServiceNode is a service node
type ServiceNode struct {
  ServiceName string
  IP     net.IP
  Port    int
  Tags    map[string]string
}

// NodeRegistry is the service node registry
type NodeRegistry interface {
  // GetNodes returns service nodes
  GetNodes(ctx context.Context, serviceName string, tags map[string]string) ([]*ServiceNode, error)
  // Register registers a service node
  Register(ctx context.Context, node *ServiceNode) error
  // Unregister deregisters a service node
  Unregister(ctx context.Context, node *ServiceNode) error
}

// MatchTags reports whether the node tags match the query tags
func MatchTags(nodeTags, queryTags map[string]string) bool {
  for name, value := range queryTags {
    if nodeTags[name] != value {
      return false
    }
  }
  return true
}
```



**Writing the Implementation**

The implementation follows a familiar pattern. GetNodes reads from the local cache first; on a miss, it queries the registry remotely and watches for node change events so the local cache stays up to date in real time. Register registers the node and sets up a heartbeat. In etcd, heartbeats are built on leases: as long as the lease is renewed periodically, the node stays alive.

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
  // DialTimeout is the default dial timeout
  DialTimeout = 5 * time.Second
  // LeaseTTL is the default lease TTL
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
  // Check the local cache for service nodes
  nodes, exists := r.nodeListMap.Load(serviceName)
  if !exists {
    var err error
    // Cache miss: pull from etcd
    nodes, err = r.pullNodes(ctx, serviceName)
    if err != nil {
      return nil, err
    }
    // Store in the local cache
    r.nodeListMap.Store(serviceName, nodes)
    // Start a goroutine to watch for node changes
    go r.watchNodes(ctx, serviceName)
  }

  // Filter service nodes by tags
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
  // Create a lease
  lease, err := r.client.Grant(ctx, int64(LeaseTTL.Seconds()))
  if err != nil {
    return err
  }
// Write the service node to etcd
  key := makeNodeKey(node)
  _, err = r.kv.Put(ctx, key, value, clientv3.WithLease(lease.ID))
  if err != nil {
    return fmt.Errorf("failed to put key to etcd: %v", err)
  }
  // Renew the lease
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

// Renew the lease
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
    nodes := value.(*sync.Map)
    nodes.Delete(makeNodeKey(node))
    return true
  })
}

func (r *registry) pullNodes(ctx context.Context, serviceName string) (*sync.Map, error) {
  resp, err := r.kv.Get(ctx, serviceName+"/", clientv3.WithPrefix())
  if err != nil {
    return nil, fmt.Errorf("failed to get nodeListMap from etcd: %v", err)
  }
  var nodes sync.Map
  for _, kv := range resp.Kvs {
    node := &discovery.ServiceNode{}
    if err := json.Unmarshal(kv.Value, node); err != nil {
      return nil, fmt.Errorf("failed to unmarshal node data: %v", err)
    }
    nodes.Store(string(kv.Key), node)
  }
  return &nodes, nil
}

 

func (r *registry) watchNodes(ctx context.Context, serviceName string) {
  watchChan := r.watcher.Watch(ctx, serviceName+"/", clientv3.WithPrefix())
  for wResp := range watchChan {
    for _, ev := range wResp.Events {
      switch ev.Type {
      case clientv3.EventTypePut:
       // Node added or updated
       node := &discovery.ServiceNode{}
       if err := json.Unmarshal(ev.Kv.Value, node); err != nil {
         log.Printf("failed to unmarshal node data: %v", err)
         continue
       }
       r.nodeListMap.LoadOrStore(serviceName, &sync.Map{})
       nodes, _ := r.nodeListMap.Load(serviceName)
       nodes.(*sync.Map).Store(string(ev.Kv.Key), node)
      case clientv3.EventTypeDelete:
       // Node removed
       nodes, _ := r.nodeListMap.Load(serviceName)
       nodes.(*sync.Map).Delete(string(ev.Kv.Key))
      }
    }
  }
}
```
The registry struct implements the discovery.NodeRegistry interface and manages service nodes in the microservices architecture. It contains a node map, nodes, which caches service node information, and an etcd client, client, which communicates with the etcd cluster.

NewRegistry initializes the etcd client and creates a registry instance. It takes a list of etcd endpoints and configures the client to connect to the etcd cluster.

GetNodes returns the list of service nodes for a given service name. If the local cache has no nodes for that service, it pulls them from etcd and starts a goroutine, watchNodes, to watch for changes to the service's nodes in etcd.

Register lets a service node register itself with etcd and creates a lease to keep the registration valid. It also starts a goroutine, keepLeaseAlive, to renew the lease so the node information does not expire.

Unregister deregisters a service node from etcd and updates the local cache.

keepLeaseAlive renews the lease periodically so the node's registration in etcd does not expire.

removeNode removes a deregistered node from the local cache.

pullNodes pulls service node information from etcd and deserializes it into a list of ServiceNode objects.

watchNodes watches for service node change events in etcd and updates the local cache.

**Writing Unit Tests**

In a microservices architecture, the stability and reliability of the service registry are critical to the whole system. To make sure our etcd registry correctly handles registering, querying, and deregistering service nodes, we wrote a set of unit tests to verify its behavior. The tests cover not only registering and deregistering a single node but also scenarios with multiple nodes and multiple tags, ensuring the discovery logic works correctly in a variety of situations.

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
    node := &discovery.ServiceNode{
      ServiceName: "test",
      IP:     net.IPv4(127, 0, 0, 1),
      Port:    8484,
      Tags: map[string]string{
       "version": "1.0",
      },
    }
    // Register nodes
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
    // Unregister nodes
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
  t.Run("Register multi nodes with multi tags", func(t *testing.T) {
    node1 := &discovery.ServiceNode{
      ServiceName: "test",
      IP:     net.IPv4(127, 0, 0, 1),
      Port:    8484,
      Tags: map[string]string{
       "version": "1.0",
       "region": "cn",
      },
    }
    node2 := &discovery.ServiceNode{
      ServiceName: "test",
      IP:     net.IPv4(127, 0, 0, 2),
      Port:    8484,
      Tags: map[string]string{
       "version": "1.0",
       "region": "us",
      },
    }
    // Register nodes
    err = r.Register(context.Background(), node1)
    a.Nil(err)
    err = r.Register(context.Background(), node2)
    a.Nil(err)
    time.Sleep(time.Millisecond * 100)
    // Get nodes
    nodes, err := r.GetNodes(context.Background(), "test", map[string]string{
      "version": "1.0",
      "region": "cn",
    })
    a.Nil(err)
    a.Len(nodes, 1)
    a.Equal(node1, nodes[0])
    // Get nodes
    nodes, err = r.GetNodes(context.Background(), "test", map[string]string{
      "version": "1.0",
      "region": "us",
    })
    a.Nil(err)
    a.Len(nodes, 1)
    a.Equal(node2, nodes[0])
    // Get nodes
    nodes, err = r.GetNodes(context.Background(), "test", nil)
    a.Nil(err)
    a.Len(nodes, 2)
    // Unregister nodes
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
Note that the test code uses time.Sleep to block the goroutine. Node watching runs asynchronously in a separate goroutine, so the main goroutine has to wait for that code to finish updating the local node cache before the assertions can pass.

This section covered an etcd-based service registry in detail, from initializing the client and registering and deregistering service nodes to querying and watching them. Building on etcd's powerful distributed key-value storage, we created a highly available, consistent service discovery mechanism. The tests verified that the registry behaves correctly and reliably with both single and multiple nodes, ensuring the data used for service discovery is accurate and up to date. After this section, you should understand not only the key role etcd plays in service discovery but also how to use it for service registration and discovery in a real project.



Upcoming posts will cover service discovery and registry implementations based on Consul and Zookeeper.
