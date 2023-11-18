---
slug: build-a-linux-c-development-environment-based-on-docker-vscode
title: Build a linux/c++ development environment based on docker/vscode step-by-step
date: 2023-10-20 20:52:05
categories:
- Engineering
tags:
- C++
alias:
- /2023/10/20/Build-a-linux-c-development-environment-based-on-docker-vscode.html
---

Sometimes we want to develop some high-performance c++ application on Linux(like epoll/ioturing), installing a virtual machine is a solution, but I think it's not the most convenient solution, today I'll share how to build a linux/c++ development environment based on docker/vscode.

<!--more-->

## Principle

+ Windows/macOs support the [Docker](https://www.docker.com/) platform with which you can run any linux-based image. So we can install docker engine and launch an image(like Ubuntu), install any linux software like a real Linux system, boost, protobuf, ...
+ [Visual Studio Code(known as VSCode)](https://code.visualstudio.com/) is a powerfull IDE which has a huge number of extensions, and Microsoft provider a official solution to make Remote Development(SSH, Docker, ...), so we can attach to a running container launched by Docker to do anything like a normal Linux!

## Step

Let's start to build a full-feature linux/c++ development environment from scratch!

### Install Docker

1. Download  Docker from https://www.docker.com/get-started/ base on your OS.

2. Install docker and launch it

3. Open a terminal(linux/macos) or PowerShell/CMD(Windows)

4. Execute the following command to **launch** a Ubuntu:22.04 image, this is the latest Ubuntu LTS Image.

   *This may take some time to download image, just be patient.*

   ```bash
   docker run -itd --name LinuxDevelop ubuntu:22.04
   ```

5. After the command return, you can see a hash, then go to step 6.

6. Execute the following command to attach in the Ubuntu container.

   ```bash
   docker exec -it LinuxDevelop /bin/bash
   ```

7. After attached to the container, execute the following command to install essential software.

   ```bash
   apt-get update
   apt-get install build-essential cmake git vim -y
   ```

8. Create a C++ file with the following code, which can tell us whether the c++ works.

   ```bash
   #include <iostream>
   
   int main()
   {
           std::cout << __cplusplus << std::endl;
           return 0;
   }
   ```

9. Execute the following command to compile this program.

   ```bash
   g++ -std=c++17 test.cc
   ```

10. Then you can see `a.out` in your current dictory, just execute it.

    ```bash
    ./a.bout
    201703
    ```

11. Congradulations!Your linux/c++ environment is working! Execute the following command to detatch from the current container. Because we need to execute docker command on our host to save this image.

12. Execute the following command on your **Host Terminal**.

    ```bash
    docker commit LinuxDevelop linux_develop:1.0
    ```

13. Yes, you get a durable image of a linux/c++ development environment.

### Install Visual Studio Code

1. Go to https://code.visualstudio.com/ download Visual Studio Code based on Your OS.

2. Install Visual Studio Code and launch it.

3. Install the Remote Development Extension.

4. ![image-20231020212527112](https://raw.githubusercontent.com/xialeistudio/picture-bucket/main/blog/image-20231020212527112.png)

5. After you have installed the extension, you can see a Remote Explorer, attach to your Ubuntu container.

   ![image-20231020213850965](https://raw.githubusercontent.com/xialeistudio/picture-bucket/main/blog/image-20231020213850965.png)

6. Visual Studio Code will automatically download some application in your Docker container.

7. Install C++ Extension

   ![image-20231020214434083](https://raw.githubusercontent.com/xialeistudio/picture-bucket/main/blog/image-20231020214434083.png)

8. Enjoy your development in this Visual Studio Code like your local development, in which you can  aslo launch Terminal.

### Test

Let's build a boost-based application.

1. Open terminal in Visual Studio Code and run the following command.

   ```bash
   apt-get install libboost-dev -y
   ```

2. Create a cpp file `main.cc` with the following code.

   ```c++
   #include <boost/log/trivial.hpp>
   
   int main(int, char *[])
   {
       BOOST_LOG_TRIVIAL(trace) << "A trace severity message";
       BOOST_LOG_TRIVIAL(debug) << "A debug severity message";
       BOOST_LOG_TRIVIAL(info) << "An informational severity message";
       BOOST_LOG_TRIVIAL(warning) << "A warning severity message";
       BOOST_LOG_TRIVIAL(error) << "An error severity message";
       BOOST_LOG_TRIVIAL(fatal) << "A fatal severity message";
   
       return 0;
   }
   ```

3. Compile and run

   ```bash
   g++ -std=c++17 main.cc
   ./a.out
   
   # output
   107400
   ```

   
