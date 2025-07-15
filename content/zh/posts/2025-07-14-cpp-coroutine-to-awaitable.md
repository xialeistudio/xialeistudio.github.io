---
title: "C++ 协程进阶：将 std::future 转换为 asio::awaitable"
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

在现代 C++ 开发中，协程为异步编程带来了革命性的改变。然而，在使用 boost::asio 或 standalone asio 时，我们经常遇到需要将传统的 `std::future<T>` 转换为 `asio::awaitable<T>` 的场景。本文将详细介绍一种高效、线程安全的转换方法。

<!--more-->

## 问题背景

在使用 asio 协程时，我们经常遇到这样的场景：
- 需要调用返回 `std::future` 的第三方库（如数据库驱动）
- 希望在协程中使用 `co_await` 来处理这些异步操作
- 不希望阻塞 IO 线程，保持高性能

传统的解决方案可能会使用定时器轮询或直接在 IO 线程中调用 `future.get()`，这些方法要么效率低下，要么会阻塞 IO 线程。

## 核心解决方案

我们的解决方案基于 `asio::async_initiate`，它提供了与 asio 协程系统的完美集成，同时避免了阻塞 IO 线程的问题。

### 核心实现

```cpp
#include <asio.hpp>
#include <future>
#include <optional>
#include <tuple>

// 线程池用于处理阻塞操作
asio::thread_pool blocking_pool(4);

// 将 std::future<T> 转换为 asio::awaitable<T>
template<typename T, typename CompletionToken>
auto future_to_awaitable(std::future<T> future, CompletionToken&& token) {
    return asio::async_initiate<CompletionToken, void(std::tuple<std::optional<T>, std::exception_ptr>)>(
        [future = std::move(future)](auto&& handler) mutable {
            auto executor = asio::get_associated_executor(handler);
            
            // 在线程池中执行阻塞操作，避免阻塞 IO 线程
            asio::post(blocking_pool, [future = std::move(future), handler = std::move(handler), executor]() mutable {
                std::tuple<std::optional<T>, std::exception_ptr> result;
                
                try {
                    T value = future.get();
                    result = std::make_tuple(std::make_optional(std::move(value)), nullptr);
                } catch (...) {
                    result = std::make_tuple(std::nullopt, std::current_exception());
                }
                
                // 回到原始执行器上下文中调用 handler
                asio::post(executor, [handler = std::move(handler), result = std::move(result)]() mutable {
                    handler(std::move(result));
                });
            });
        },
        token
    );
}

// 协程专用的包装函数
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

## 使用示例

### 基本使用

```cpp
// 模拟数据库查询
std::future<std::string> query_mysql(const std::string& sql) {
    return std::async(std::launch::async, [sql] {
        std::this_thread::sleep_for(std::chrono::seconds(1));
        return "Query result for: " + sql + " - Found 10 rows";
    });
}

// 在协程中使用
asio::awaitable<void> example_coro() {
    try {
        // 直接在协程中 await future
        auto result = co_await await_future(query_mysql("SELECT * FROM users"));
        std::cout << "Query successful: " << result << std::endl;
    } catch (const std::exception& e) {
        std::cout << "Query failed: " << e.what() << std::endl;
    }
}
```

### 异常处理

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

## 技术要点分析

### 1. 使用 `async_initiate` 的优势

- **完美集成**：与 asio 协程系统无缝集成
- **类型安全**：编译时类型检查
- **性能优化**：避免了定时器轮询的开销

### 2. 线程池设计

```cpp
asio::thread_pool blocking_pool(4);
```

- 专门用于处理阻塞操作
- 避免阻塞 IO 线程
- 可根据需要调整线程数量

### 3. 异常处理策略

使用 `std::tuple<std::optional<T>, std::exception_ptr>` 来处理两种情况：
- 正常结果：`{std::optional<T>, nullptr}`
- 异常情况：`{std::nullopt, std::exception_ptr}`

这种设计能够正确处理边界情况，比如返回类型本身就是 `std::exception_ptr` 的情况。

### 4. 执行器上下文保持

```cpp
auto executor = asio::get_associated_executor(handler);
// ...
asio::post(executor, [handler = std::move(handler), result = std::move(result)]() mutable {
    handler(std::move(result));
});
```

确保最终的 handler 调用在正确的执行器上下文中进行，保持了 asio 的执行器语义。

## 性能考虑

1. **避免 IO 线程阻塞**：所有阻塞操作都在独立的线程池中执行
2. **移动语义**：大量使用 `std::move` 避免不必要的拷贝
3. **零拷贝设计**：结果直接在线程间传递，无需额外拷贝

## 实际应用场景

这种转换方法特别适合以下场景：

1. **数据库操作**：将数据库驱动的异步接口转换为协程友好的形式
2. **文件 I/O**：处理可能阻塞的文件操作
3. **第三方库集成**：与返回 `std::future` 的库进行集成
4. **计算密集型任务**：将 CPU 密集型任务转换为可 await 的形式

## 总结

通过使用 `asio::async_initiate` 和线程池，我们实现了一个高效、线程安全的 `std::future` 到 `asio::awaitable` 的转换方案。这种方法不仅避免了阻塞 IO 线程，还提供了完美的异常处理机制，是现代 C++ 异步编程的最佳实践之一。

这种设计模式可以轻松扩展到其他异步场景，为构建高性能的协程应用奠定了坚实的基础。 