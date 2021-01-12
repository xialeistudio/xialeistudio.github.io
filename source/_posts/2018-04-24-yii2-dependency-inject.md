---
title: 使用yii2依赖注入规范业务开发
date: 2018-04-24 22:18:04
categories: 
- backend
- php
tags:
- yii
---

## 本文代码

[https://github.com/xialeistudio/yii2-di-demo](https://github.com/xialeistudio/yii2-di-demo)

## 什么是依赖注入(DI)?

对象由框架来创建而不是程序员通过 **new** 创建。跟IoC差不多一个意思。

## 为什么要有依赖注入?

1. 解耦。调用方不再通过 **new** 运算符实例化被调用对象，而通过框架(IoC容器)创建之后注入进来。解除了调用者与被调用者之间的依赖。
2. 有利于面向接口编程。个人认为OOP程序设计最重要的就是面向接口(面向抽象)编程。因为有了第1步的关系，调用者只需要依赖接口类型而不用依赖实现类型，提高了程序的扩展性。

## Yii2的依赖注入

Yii2通过 [yii\di\Container](http://www.yiichina.com/doc/api/2.0/yii-di-container) 提供DI容器特性。目前支持一下4种方式注入：

1. [构造方法注入](http://www.yiichina.com/doc/guide/2.0/concept-di-container#constructor-injection)
2. [方法注入](http://www.yiichina.com/doc/guide/2.0/concept-di-container#constructor-injection)
3. [Setter和属性注入](http://www.yiichina.com/doc/guide/2.0/concept-di-container#constructor-injection)
4. [PHP回调注入](http://www.yiichina.com/doc/guide/2.0/concept-di-container#constructor-injection)

## 注册依赖关系

1. 通过容器的 **set** 方法注入
2. 通过配置文件注入(推荐)

## 依赖注入实战

1. 打开终端，执行以下命令初始化项目：

    ```bash
    composer create-project --prefer-dist yiisoft/yii2-app-basic basic
    ```

2. 声明接口业务类 **app\services\UserService**

    ```php
    <?php
    /**
    * Created by PhpStorm.
    * User: xialei
    * Date: 2018/4/24
    * Time: 下午10:55
    */

    namespace app\services;

    /**
    * 用户业务类
    * Interface UserService
    * @package app\services
    */
    interface UserService
    {
        /**
        * 根据ID查询用户
        * @param integer $id
        * @return array|null
        */
        public function show($id);

        /**
        * 查看所有用户
        * @return array
        */
        public function all();
    }
    ```

3. 接口实现文件 **app\services\impl\UserServiceImpl**

    ```php
    <?php
    /**
    * Created by PhpStorm.
    * User: xialei
    * Date: 2018/4/24
    * Time: 下午10:56
    */

    namespace app\services\impl;


    use app\services\UserService;

    class UserServiceImpl implements UserService
    {
        private $users = [
            ['id' => 1, 'name' => 'xialei'],
            ['id' => 2, 'name' => 'zhangsan'],
        ];

        /**
        * 根据ID查询用户
        * @param integer $id
        * @return array
        */
        public function show($id)
        {
            foreach ($this->users as $user) {
                if ($user['id'] == $id) {
                    return $user;
                }
            }
            return null;
        }

        /**
        * 查看所有用户
        * @return array
        */
        public function all()
        {
            return $this->users;
        }
    }
    ```

4. 注册依赖关系 **config/web.php**

    ```php
    <?php

    use app\services\UserService;
    use app\services\impl\UserServiceImpl;

    $params = require __DIR__ . '/params.php';
    $db = require __DIR__ . '/db.php';

    $config = [
        'id' => 'basic',
        'basePath' => dirname(__DIR__),
        'bootstrap' => ['log'],
        'aliases' => [
            '@bower' => '@vendor/bower-asset',
            '@npm' => '@vendor/npm-asset',
        ],
        'container' => [
            'definitions' => [
                UserService::class => UserServiceImpl::class
            ]
        ],
        'components' => [
            'request' => [
                // !!! insert a secret key in the following (if it is empty) - this is required by cookie validation
                'cookieValidationKey' => '0xGrStOOZE2oXxNNiu-o2eYovJ_Ia1Dk',
            ],
            'response' => [
                'format' => 'json'
            ],
            'errorHandler' => [
                'errorAction' => 'site/error',
            ],
            'urlManager' => [
                'enablePrettyUrl' => true,
                'showScriptName' => false,
                'rules' => [
                ],
            ],
        ],
    ];

    if (YII_ENV_DEV) {
        // configuration adjustments for 'dev' environment
        $config['bootstrap'][] = 'debug';
        $config['modules']['debug'] = [
            'class' => 'yii\debug\Module',
            // uncomment the following to add your IP if you are not connecting from localhost.
            //'allowedIPs' => ['127.0.0.1', '::1'],
        ];

        $config['bootstrap'][] = 'gii';
        $config['modules']['gii'] = [
            'class' => 'yii\gii\Module',
            // uncomment the following to add your IP if you are not connecting from localhost.
            //'allowedIPs' => ['127.0.0.1', '::1'],
        ];
    }

    return $config;
    ```

5. 添加控制器 **app\controllers\UserController**

    ```php
    <?php
    /**
    * Created by PhpStorm.
    * User: xialei
    * Date: 2018/4/24
    * Time: 下午10:57
    */

    namespace app\controllers;


    use app\services\UserService;
    use yii\base\Module;
    use yii\web\Controller;
    use yii\web\NotFoundHttpException;

    class UserController extends Controller
    {
        private $userService;

        public function __construct(string $id, Module $module, UserService $userService, array $config = [])
        {
            $this->userService = $userService;
            parent::__construct($id, $module, $config);
        }

        /**
        * 查看用户
        * @param $id
        * @return array|null
        * @throws NotFoundHttpException
        */
        public function actionShow($id)
        {
            $user = $this->userService->show($id);
            if (empty($user)) {
                throw new NotFoundHttpException('用户不存在');
            }
            return $user;
        }

        /**
        * 查看所有用户
        * @return array
        */
        public function actionAll()
        {
            return $this->userService->all();
        }
    }
    ```

6. 运行测试服务器

    ```bash
    ./yii serve/index
    ```

7. 访问用户列表接口 [http://localhost:8080/user/all](http://localhost:8080/user/all)

    ```json
    [{
        "id": 1,
        "name": "xialei"
    }, {
        "id": 2,
        "name": "zhangsan"
    }]
    ```

8. 访问查看用户接口 [http://localhost:8080/user/show?id=1](http://localhost:8080/user/show?id=1)

    ```json
    {
        "id": 1,
        "name": "xialei"
    }
    ```

## 写在最后

如你所见，Yii2自带的IoC容器使用起来还是挺方便的，观测了Yii **配置优于编码** 的思想，Yii的组件基本上都可以在配置文件中进行配置而不需要手动编码。

灵活使用DI可以使我们从依赖关系中解脱出来，专注于业务逻辑。

当然，业务逻辑的组织也是一个很大的研究课题，有兴趣的可以去看看 **DDD(领域驱动设计)**