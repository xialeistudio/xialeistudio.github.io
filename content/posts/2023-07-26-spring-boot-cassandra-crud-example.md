---
slug: spring-boot-cassandra-crud-example
title: Spring Boot Cassandra CRUD Example
date: 2023-07-26 12:00:18
categories:
- engineering
tags:
- cassandra
---

[Apache Cassandra](https://cassandra.apache.org/) is an **open source** NoSQL distributed database trusted by thousands of companies for **scalability** and **high availability** without compromising performance. **Linear scalability** and **proven fault-tolerance** on **commodity hardware** or **cloud infrastructure** make it the perfect platform for **mission-critical** data.

In this article, I'll share a whole project to demonstrate how to perform CRUD operation in Cassandra with Spring Boot.

*Note: Pagination in Cassandra is a little tricky, Cassandra don't support offset-based limit, so we need to use cursor-based limit to implement pagination.*

## Project Source Code

**database setup**

Just following the [Quick Start](https://cassandra.apache.org/_/quickstart.html) of Cassandra official document to install a local Cassandra instance in Docker. Since we use Spring Data Cassandra to operate Cassandra, there is no DDL required. 

**pom.xml**

I use the Spring Initializer to create a simple project with **web and cassandra** starter. This is the content of pom.xml.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>3.1.2</version>
        <relativePath/> <!-- lookup parent from repository -->
    </parent>
    <groupId>com.example</groupId>
    <artifactId>cassandra-timeline</artifactId>
    <version>0.0.1-SNAPSHOT</version>
    <name>cassandra-timeline</name>
    <description>cassandra-timeline</description>
    <properties>
        <java.version>17</java.version>
    </properties>
    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-data-cassandra</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>

        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <scope>test</scope>
        </dependency>
    </dependencies>

    <build>
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
            </plugin>
        </plugins>
    </build>

</project>
```

**CassandraApplication.java**

```java
package com.example.cassandratimeline;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class CassandraApplication {

    public static void main(String[] args) {
        SpringApplication.run(CassandraApplication.class, args);
    }
}
```

**application.yml**

```yaml
spring:
  cassandra:
    schema-action: CREATE_IF_NOT_EXISTS
    local-datacenter: datacenter1
    keyspace-name: spring_cassandra
```

**Vet.java**

**Vet** is our core model definition. In this example, I just set the partition key (id) to a fixed number to ensure that all data is in the same partition, so we can get automatically sorted data, which is not a best practice, it's just for demonstration.

```java
package com.example.cassandratimeline;

import java.time.LocalDateTime;
import java.util.Set;
import org.springframework.data.cassandra.core.cql.Ordering;
import org.springframework.data.cassandra.core.cql.PrimaryKeyType;
import org.springframework.data.cassandra.core.mapping.PrimaryKeyColumn;
import org.springframework.data.cassandra.core.mapping.Table;

@Table
public class Vet {

    @PrimaryKeyColumn(ordinal = 0, type = PrimaryKeyType.PARTITIONED)
    private int id;

    private String firstName;
    private String lastName;
    private Set<String> specialties;

  	// cluster key, so we can get automatically sorted data
    @PrimaryKeyColumn(ordinal = 1, type = PrimaryKeyType.CLUSTERED, ordering = Ordering.DESCENDING, value = "created_at")
    private LocalDateTime createdAt;

    public Vet(int id, String firstName, String lastName, Set<String> specialties, LocalDateTime createdAt) {
        this.id = id;
        this.firstName = firstName;
        this.lastName = lastName;
        this.specialties = specialties;
        this.createdAt = createdAt;
    }

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(LocalDateTime createdAt) {
        this.createdAt = createdAt;
    }

    public int getId() {
        return id;
    }

    public void setId(int id) {
        this.id = id;
    }

    public String getFirstName() {
        return firstName;
    }

    public void setFirstName(String firstName) {
        this.firstName = firstName;
    }

    public String getLastName() {
        return lastName;
    }

    public void setLastName(String lastName) {
        this.lastName = lastName;
    }

    public Set<String> getSpecialties() {
        return specialties;
    }

    public void setSpecialties(Set<String> specialties) {
        this.specialties = specialties;
    }
}

```

**VetRepository.java**

```java
package com.example.cassandratimeline;

import java.util.UUID;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Slice;
import org.springframework.data.repository.CrudRepository;

public interface VetRepository extends CrudRepository<Vet, UUID> {
    Slice<Vet> findAll(Pageable pageable);
}
```

**VetController.java**

Cassandra don't support offset-based limit, so the following code uses a cursor-based limit to implement pagination.

Cassandra returns a `PageState` of `ByteBuffer`, so we need to encode it to Base64 string to achive transimition in the URL.

```java
package com.example.cassandratimeline;

import java.nio.ByteBuffer;
import java.time.LocalDateTime;
import java.util.Base64;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import org.springframework.data.cassandra.core.query.CassandraPageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/vet")
public class VetController {

    private final VecRepository repository;

    public VetController(VecRepository repository) {
        this.repository = repository;
    }

    @PostMapping("/create")
    public Vet create(@RequestBody Vet vet) {
        vet.setId(1); // Demonstration Only, Bad Practice
        vet.setCreatedAt(LocalDateTime.now());
        repository.save(vet);
        return vet;
    }

    @PostMapping("/update")
    public Vet update(@RequestBody Vet vet, @RequestParam("id") UUID id) {
        Optional<Vet> optionalVet = repository.findById(id);
        if (optionalVet.isEmpty()) {
            throw new RuntimeException("not found");
        }
        Vet vet1 = optionalVet.get();
        vet1.setFirstName(vet.getFirstName());
        vet1.setLastName(vet.getLastName());
        vet1.setSpecialties(vet.getSpecialties());
        repository.save(vet1);
        return vet1;
    }

    @GetMapping("show")
    public Vet show(@RequestParam("id") UUID id) {
        Optional<Vet> optionalVet = repository.findById(id);
        if (optionalVet.isEmpty()) {
            throw new RuntimeException("not found");
        }
        return optionalVet.get();
    }

    @GetMapping("list")
    public Map<String, Object> showAll(@RequestParam(value = "page_state", defaultValue = "") String pageState, @RequestParam(value = "size", defaultValue = "10") int size) {
        var pagingState = pageState.isEmpty() ? null : ByteBuffer.wrap(Base64.getUrlDecoder().decode(pageState));
        var pageable = CassandraPageRequest.of(Pageable.ofSize(size), pagingState);
        var result = repository.findAll(pageable);
        var nextPageState = ((CassandraPageRequest) result.getPageable()).getPagingState();
        var nextPageStateData = "";
        if (nextPageState != null) {
            var bytes = new byte[nextPageState.remaining()];
            nextPageState.get(bytes, 0, bytes.length);
            nextPageStateData = Base64.getUrlEncoder().encodeToString(bytes);
        }
        return Map.of("errcode", 0, "errmsg", "ok", "list", result.getContent(), "pageState", nextPageStateData);
    }

    @GetMapping("/delete-all")
    public Map<String, Object> deleteAll() {
        repository.deleteAll();
        return Map.of("errcode", 0, "errmsg", "ok");
    }
}
```

## Testing

I use Postman and Chrome to test this project.

**Create**

```
---REQUEST---
POST localhost:8080/vet/create
Content-Type: application/json

{
    "firstName":"Foo",
    "lastName":"Bar",
    "specialties":[
        "a","b","c"
    ]
}

---RESPONSE---
{
    "id": 1,
    "firstName": "Foo",
    "lastName": "Bar",
    "specialties": [
        "a",
        "b",
        "c"
    ],
    "createdAt": "2023-07-26T12:18:26.868478"
}
```

**Pagination1**

```text
---REQUEST---
GET http://localhost:8080/vet/list?size=2

---RESPONSE---
{
    "pageState":"BAAAAAEKAAgAAAGJkGw-KPB____98H____0=",
    "errmsg":"ok",
    "list":[
        {
            "id":1,
            "firstName":"Foo",
            "lastName":"Bar",
            "specialties":[
                "a",
                "b",
                "c"
            ],
            "createdAt":"2023-07-26T12:19:20.985"
        },
        {
            "id":1,
            "firstName":"Foo",
            "lastName":"Bar",
            "specialties":[
                "a",
                "b",
                "c"
            ],
            "createdAt":"2023-07-26T12:19:20.232"
        }
    ],
    "errcode":0
}
```

**Pagination2**

```text
---REQUEST---
GET http://localhost:8080/vet/list?size=2&page_state=BAAAAAEKAAgAAAGJkGw-KPB____98H____0=

---RESPONSE---
{
    "pageState":"BAAAAAEKAAgAAAGJkGw3nfB____78H____s=",
    "errmsg":"ok",
    "list":[
        {
            "id":1,
            "firstName":"Foo",
            "lastName":"Bar",
            "specialties":[
                "a",
                "b",
                "c"
            ],
            "createdAt":"2023-07-26T12:19:19.457"
        },
        {
            "id":1,
            "firstName":"Foo",
            "lastName":"Bar",
            "specialties":[
                "a",
                "b",
                "c"
            ],
            "createdAt":"2023-07-26T12:19:18.557"
        }
    ],
    "errcode":0
}
```

As you can see, the page_state works as expected.

## Reference

+ [Get Started with Apache Cassandra](https://cassandra.apache.org/_/quickstart.html)
