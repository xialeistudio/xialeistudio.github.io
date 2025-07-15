---
title: "C++ Coroutines Advanced: Converting std::future to asio::awaitable"
date: 2025-07-15T09:00:00+08:00
slug: cpp-coroutine-future-to-awaitable
categories: 
- Engineering
tags:
- cpp
- coroutine
- asio
- future
featured: true
---

In modern C++ development, coroutines have brought revolutionary changes to asynchronous programming. However, when using boost::asio or standalone asio, we often encounter scenarios where we need to convert traditional `std::future<T>` to `asio::awaitable<T>`. This article will detail an efficient, thread-safe conversion method.

<!--more-->

## Problem Background

When using asio coroutines, we often encounter scenarios like:
- Need to call third-party libraries that return `std::future` (such as database drivers)
- Want to use `co_await` in coroutines to handle these asynchronous operations
- Don't want to block IO threads, maintaining high performance

Traditional solutions might use timer polling or directly call `future.get()` in IO threads, but these methods are either inefficient or block IO threads.

## Core Solution

Our solution is based on `asio::async_initiate`, which provides perfect integration with the asio coroutine system while avoiding the problem of blocking IO threads.

### Core Implementation

```cpp
#include <asio.hpp>
#include <future>
#include <optional>
#include <tuple>

// Thread pool for handling blocking operations
asio::thread_pool blocking_pool(4);

// Convert std::future<T> to asio::awaitable<T>
template<typename T, typename CompletionToken>
auto future_to_awaitable(std::future<T> future, CompletionToken&& token) {
    return asio::async_initiate<CompletionToken, void(std::tuple<std::optional<T>, std::exception_ptr>)>(
        [future = std::move(future)](auto&& handler) mutable {
            auto executor = asio::get_associated_executor(handler);
            
            // Execute blocking operation in thread pool to avoid blocking IO thread
            asio::post(blocking_pool, [future = std::move(future), handler = std::move(handler), executor]() mutable {
                std::tuple<std::optional<T>, std::exception_ptr> result;
                
                try {
                    T value = future.get();
                    result = std::make_tuple(std::make_optional(std::move(value)), nullptr);
                } catch (...) {
                    result = std::make_tuple(std::nullopt, std::current_exception());
                }
                
                // Return to original executor context to call handler
                asio::post(executor, [handler = std::move(handler), result = std::move(result)]() mutable {
                    handler(std::move(result));
                });
            });
        },
        token
    );
}

// Wrapper function specifically for coroutines
template<typename T>
asio::awaitable<T> await_future(std::future<T> future) {
    auto [result, exception] = co_await future_to_awaitable(std::move(future), asio::use_awaitable);
    
    if (exception) {
        std::rethrow_exception(exception);
    }
    
    if (result) {
        co_return std::move(*result);
    }
    
    throw std::runtime_error("Unknown error: no result and no exception");
}
```

## Usage Examples

### Basic Usage

```cpp
// Simulate database query
std::future<std::string> query_mysql(const std::string& sql) {
    return std::async(std::launch::async, [sql] {
        std::this_thread::sleep_for(std::chrono::seconds(1));
        return "Query result for: " + sql + " - Found 10 rows";
    });
}

// Use in coroutine
asio::awaitable<void> example_coro() {
    try {
        // Directly await future in coroutine
        auto result = co_await await_future(query_mysql("SELECT * FROM users"));
        std::cout << "Query successful: " << result << std::endl;
    } catch (const std::exception& e) {
        std::cout << "Query failed: " << e.what() << std::endl;
    }
}
```

### Exception Handling

```cpp
std::future<std::string> query_with_error(const std::string& sql) {
    return std::async(std::launch::async, [sql]() -> std::string {
        std::this_thread::sleep_for(std::chrono::seconds(1));
        throw std::runtime_error("Database connection failed");
    });
}

asio::awaitable<void> error_handling_example() {
    try {
        auto result = co_await await_future(query_with_error("SELECT * FROM invalid_table"));
        std::cout << "Should not reach here" << std::endl;
    } catch (const std::exception& e) {
        std::cout << "Exception caught: " << e.what() << std::endl;
    }
}
```

## Technical Points Analysis

### 1. Advantages of Using `async_initiate`

- **Perfect Integration**: Seamlessly integrates with asio coroutine system
- **Type Safety**: Compile-time type checking
- **Performance Optimization**: Avoids timer polling overhead

### 2. Thread Pool Design

```cpp
asio::thread_pool blocking_pool(4);
```

- Dedicated to handling blocking operations
- Avoids blocking IO threads
- Thread count can be adjusted as needed

### 3. Exception Handling Strategy

Using `std::tuple<std::optional<T>, std::exception_ptr>` to handle two scenarios:
- Normal result: `{std::optional<T>, nullptr}`
- Exception case: `{std::nullopt, std::exception_ptr}`

This design correctly handles edge cases, such as when the return type itself is `std::exception_ptr`.

### 4. Executor Context Preservation

```cpp
auto executor = asio::get_associated_executor(handler);
// ...
asio::post(executor, [handler = std::move(handler), result = std::move(result)]() mutable {
    handler(std::move(result));
});
```

Ensures that the final handler call occurs in the correct executor context, maintaining asio's executor semantics.

## Performance Considerations

1. **Avoid IO Thread Blocking**: All blocking operations are executed in independent thread pools
2. **Move Semantics**: Extensive use of `std::move` to avoid unnecessary copying
3. **Zero-Copy Design**: Results are passed directly between threads without additional copying

## Practical Application Scenarios

This conversion method is particularly suitable for the following scenarios:

1. **Database Operations**: Converting database driver async interfaces to coroutine-friendly forms
2. **File I/O**: Handling potentially blocking file operations
3. **Third-Party Library Integration**: Integrating with libraries that return `std::future`
4. **CPU-Intensive Tasks**: Converting CPU-intensive tasks to awaitable forms

## Summary

By using `asio::async_initiate` and thread pools, we've implemented an efficient, thread-safe solution for converting `std::future` to `asio::awaitable`. This approach not only avoids blocking IO threads but also provides perfect exception handling mechanisms, making it one of the best practices for modern C++ asynchronous programming.

This design pattern can be easily extended to other asynchronous scenarios, laying a solid foundation for building high-performance coroutine applications. 