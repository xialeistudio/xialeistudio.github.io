---
title: How to retry requests correctly with Feign
date: 2023-05-05 11:46:27
categories:
- engineering
tags:
- java
---

Network is unstable, it can fail at any moment. In this article, I'll share how to retry requests correctly with Feign.

> [Feign](https://github.com/OpenFeign/feign/) is a Java to HTTP client binder inspired by [Retrofit](https://github.com/square/retrofit), [JAXRS-2.0](https://jax-rs-spec.java.net/nonav/2.0/apidocs/index.html), and [WebSocket](http://www.oracle.com/technetwork/articles/java/jsr356-1937161.html). Feign's first goal was reducing the complexity of binding [Denominator](https://github.com/Netflix/Denominator) uniformly to HTTP APIs regardless of [ReSTfulness](http://www.slideshare.net/adrianfcole/99problems).
>
> ***[Feign](https://github.com/OpenFeign/feign/#error-handling)*** - Introduction

<!--more-->

## Terms

### ErrorDecoder

[ErrorDecoder](https://github.com/OpenFeign/feign/#error-handling) is a interface in Feign to decode an Exception, you can modify the return exception type of `decode` method, we usually implement retry in conjunction with `ErrorDecoder` with `Retryer`.  

The following code shows the definition of `ErrorDecoder`.

```java
public interface ErrorDecoder {
  Exception decode(String methodKey, Response response);
}
```

### Retryer

> Feign, by default, will automatically retry `IOException`s, regardless of HTTP method, treating them as transient network related exceptions, and any `RetryableException` thrown from an `ErrorDecoder`. 
>
> ***[Feign](https://github.com/OpenFeign/feign/#error-handling)*** - [Retryer](https://github.com/OpenFeign/feign/#retry)

In `Retryer`, we need to override `continueOrPropagate` method to do some retry work, there are 2 execution flows:

1. If no exception thrown, Feign will retry a new request
2. If any exception thrown, Feign will stop to retry

## Situation

Imaging you are developing a feature: when we get a 401 response from server, we need to refresh our access_token and then request again. This is all transparent and has no impact on the end user.

How do we solve this problem?

Simply, we need to get a new access_token by a new request and then set the access_token to the header of the failed request, so the next request can be succeed.

## Solution 

401 response usually throws a `UnauthorizedException`, it's not an `IOException` so Feign will not retry. 

We can implement `ErrorDecoder` to return a `RetryableException` so Feign will retry our request, and we need implement a `Retryer`, modify the request parameters in `continueOrPropagate` method.

Here is a full example.

```java
public class Example {
    public static void main(String[] args) {
        var github = Feign.builder()
                .decoder(new GsonDecoder())
                .retryer(new MyRetryer(100, 3))
                .errorDecoder(new MyErrorDecoder())
                .target(Github.class, "https://api.github.com");

        var contributors = github.contributors("foo", "bar", "invalid_token");
        for (var contributor : contributors) {
            System.out.println(contributor.login + " " + contributor.contributions);
        }
    }

    static class MyErrorDecoder implements ErrorDecoder {

        private final ErrorDecoder defaultErrorDecoder = new Default();

        @Override
        public Exception decode(String methodKey, Response response) {
            // wrapper 401 to RetryableException in order to retry
            if (response.status() == 401) {
                return new RetryableException(response.status(), response.reason(), response.request().httpMethod(), null, response.request());
            }
            return defaultErrorDecoder.decode(methodKey, response);
        }
    }

    static class MyRetryer implements Retryer {

        private final long period;
        private final int maxAttempts;
        private int attempt = 1;

        public MyRetryer(long period, int maxAttempts) {
            this.period = period;
            this.maxAttempts = maxAttempts;
        }

        @Override
        public void continueOrPropagate(RetryableException e) {
            if (++attempt > maxAttempts) {
                throw e;
            }
            if (e.status() == 401) {
                // remove Authorization first, otherwise Feign will add a new Authorization header
                // cause github responses a 400 bad request
                e.request().requestTemplate().removeHeader("Authorization");
                e.request().requestTemplate().header("Authorization", "Bearer " + getNewToken());
                try {
                    Thread.sleep(period);
                } catch (InterruptedException ex) {
                    throw e;
                }
            } else {
                throw e;
            }
        }

        // Access an external api to obtain new token
        // In this example, we can simply return a fixed token to demonstrate how Retryer works
        private String getNewToken() {
            return "newToken";
        }

        @Override
        public Retryer clone() {
            return new MyRetryer(period, maxAttempts);
        }
}
```

By modify `e.request().requestTemplate()`, you can do anything you want to modify a request.

*This code example has been merged to Feign Project.*

## Reference

1. [***[Feign](https://github.com/OpenFeign/feign/#error-handling)*** - Introduction](https://github.com/OpenFeign/feign)
