---
title: Implementing timer in mio
date: 2024-03-05T09:22:56+08:00
tags: 
  - rust
categories:
  - Engineering  
featured: true
---
[Mio](https://github.com/tokio-rs/mio) is a high-performance, low-level I/O library for Rust that focuses on non-blocking APIs and event notification. While Mio provides powerful capabilities for building I/O applications, it does not include a built-in timer feature. In this article, we will explore how to implement a timer in Mio.

<!--more-->

## Core principles

The basic structure of an EventLoop-based application can be summarized as follows:

1. Create the event loop.
2. Add event callbacks, such as timers or TCP listeners.
3. Enter an infinite loop and call the `poll` function.
4. Traverse and handle the events.

During the third step, we continuously call the `poll` function in an infinite loop. If there are any triggered events, we receive a list of events. If there are no events in the current call, the `poll` function blocks until a new event occurs or a timeout is reached.

The signature of the `poll` function in Mio is as follows:

```rust
pub fn poll(&mut self, events: &mut Events, timeout: Option<Duration>) -> io::Result<()>;
```

We can pass a specific timeout, such as `Duration::from_secs(1)`, to the `poll` function. If there are no events, the `poll` function returns after 1 second. We can leverage this mechanism to implement our timer.

## Implementation

The implementation is straightforward. In each iteration of the loop, we check the current timestamp and the previous timestamp. If the time duration exceeds our desired interval, we execute the timer code (in the following example, a simple `print` statement).

```rust
fn main() -> Result<(), Box<dyn Error>> {
    let mut poll = Poll::new()?;
    let addr = "127.0.0.1:8080".parse()?;
    let mut server = TcpListener::bind(addr)?;
    poll.registry().register(&mut server, SERVER, Interest::READABLE)?;

    let mut events = Events::with_capacity(128);
    let mut next_id = 1;
    let mut last_tick = Instant::now();
    loop {
        poll.poll(&mut events, Some(Duration::from_millis(100)))?;
        let now = Instant::now();
        if now.duration_since(last_tick) > Duration::from_secs(1) {
            println!("tick {:?}", now);
            last_tick = now;
        }
        for event in events.iter() {
            match event.token() {
                SERVER => {
                    loop {
                        match server.accept() {
                            Ok((mut stream, _)) => {
                                println!("{} connected", stream.peer_addr()?);
                                let token = Token(next_id);
                                next_id += 1;
                                poll.registry().register(&mut stream, token, Interest::READABLE)?;
                            }
                            Err(ref e) if e.kind() == std::io::ErrorKind::WouldBlock => {
                                break;
                            }
                            Err(e) => {
                                eprintln!("accept error: {}", e);
                                break;
                            }
                        }
                    }
                }
                token => {
                    if event.is_readable() {
                        // handle reading event
                    }
                    if event.is_writable() {
                        // handle writing event
                    }
                }
            }
        }
    }
}
```

In this example, the `poll` function has a timeout of 100 milliseconds. Regardless of whether there are external events, our timer will execute every second.

## Conclusion

By leveraging the timeout mechanism provided by Mio's `poll` function, we can easily implement a timer in our EventLoop-based applications. This allows us to execute specific tasks at regular intervals, enhancing the functionality and versatility of our applications.

