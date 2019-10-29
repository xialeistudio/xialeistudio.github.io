# Redis优化高并发下的秒杀性能

本文内容

+ 使用Redis优化高并发场景下的接口性能
+ 数据库乐观锁

随着双11的临近，各种促销活动开始变得热门起来，比较主流的有秒杀、抢优惠券、拼团等等。

涉及到高并发争抢同一个资源的主要场景有秒杀和抢优惠券。

## 前提

活动规则

+ 奖品数量有限，比如100个
+ 不限制参与用户数
+ 每个用户只能参与1次秒杀

活动要求

+ 不能多发，也不能少发，100个奖品要全部发出去
+ 1个用户最多抢1个奖品
+ 遵循先到先得原则，先来的用户有奖品

## 数据库实现

悲观锁性能太差，本文不予讨论，讨论一下使用乐观锁解决高并发问题的优缺点。

### 数据库结构

| ID     | Code   | UserId | CreatedAt | RewardAt |
|------ | ------ | ------ | --------- | -------- |
| 奖品ID | 奖品码 | 用户ID | 创建时间  | 中奖时间 |

+ 未中奖时UserId为0，RewardAt为NULL
+ 中奖时UserId为中奖用户ID，RewardAt为中奖时间

### 乐观锁实现

乐观锁实际上并不存在真正的锁，乐观锁是利用数据的某个字段来做的，比如本文的例子就是以UserId来实现的。

实现流程如下：

1. 查询UserId为0的奖品，如果未找到则提示无奖品

   ```sql
   SELECT * FROM envelope WHERE user_id=0 LIMIT 1
   ```

2. 更新奖品的用户ID和中奖时间(假设奖品ID为1，中奖用户ID为100，当前时间为2019-10-29 12:00:00)，这里的user_id=0就是我们的乐观锁了。

   ```sql
   UPDATE envelope SET user_id=100, reward_at='2019-10-29 12:00:00' WHERE user_id=0 AND id=1
   ```

3. 检测UPDATE语句的执行返回值，如果返回1证明中奖成功，否则证明该奖品被其他人抢了

#### 为什么要添加乐观锁

正常情况下获取奖品、然后把奖品更新给指定用户是没问题的。如果不添加user_id=0时，高并发场景下会出现下面的问题：

1. 两个用户同时查询到了1个未中奖的奖品(发生并发问题)
2. 将奖品的中奖用户更新为用户1，更新条件只有ID=奖品ID
3. 上述SQL执行是成功的，影响行数也是1，此时接口会返回用户1中奖
4. 接下来将中奖用户更新为用户2，更新条件也只有ID=奖品ID
5. 由于是同一个奖品，已经发给用户1的奖品会重新发放给用户2，此时影响行数为1，接口返回用户2也中奖
6. 所以该奖品的最终结果是发放给用户2
7. `用户1就会过来投诉活动方了，因为抽奖接口返回用户1中奖，但他的奖品被抢了，此时活动方只能赔钱了`

#### 添加乐观锁之后的抽奖流程

1. 更新用户1时的条件为`id=红包ID AND user_id=0` ,由于此时红包未分配给任何人，用户1更新成功，接口返回用户1中奖
2. 当更新用户2时更新条件为`id=红包ID AND user_id=0`，由于此时该红包已经分配给用户1了，所以该条件不会更新任何记录，接口返回用户2中奖

#### 乐观锁优缺点

优点

+ 性能尚可，因为无锁
+ 不会超发

缺点

+ 通常不满足“先到先得”的活动规则，一旦发生并发，就会发生未中奖的情况，此时奖品库还有奖品

### 压测

在MacBook Pro 2018上的压测表现如下(Golang实现的HTTP服务器,MySQL连接池大小100，Jmeter压测)：

+ 500并发 500总请求数 平均响应时间331ms 发放成功数为31 吞吐量458.7/s

## Redis实现

可以看到乐观锁的实现下争抢比太高，不是推荐的实现方法，下面通过Redis来优化这个秒杀业务。

### Redis高性能的原因

+ 单线程 省去了线程切换开销
+ 基于内存的操作 虽然持久化操作涉及到硬盘访问，但是那是异步的，不会影响Redis的业务
+ 使用了IO多路复用

### 实现流程

1. 活动开始前将数据库中奖品的code写入Redis队列中

2. 活动进行时使用lpop弹出队列中的元素

3. 如果获取成功，则使用UPDATE语法发放奖品

   ```sql
   UPDATE reward SET user_id=用户ID,reward_at=当前时间 WHERE code='奖品码'
   ```

4. 如果获取失败，则当前无可用奖品，提示未中奖即可

使用Redis的情况下并发访问是通过Redis的`lpop()`来保证的，该方法是原子方法，可以保证并发情况下也是一个个弹出的。

### 压测

在MacBook Pro 2018上的压测表现如下(Golang实现的HTTP服务器,MySQL连接池大小100，Redis连接池代销100，Jmeter压测)：

+ 500并发 500总请求数 平均响应时间48ms 发放成功数100 吞吐量497.0/s

## 结论

可以看到Redis的表现是稳定的，不会出现超发，且访问延迟少了8倍左右，吞吐量还没达到瓶颈，可以看出Redis对于高并发系统的性能提升是非常大的！接入成本也不算高，值得学习！

![0.jpeg](https://static.ddhigh.com/blog/2019-10-22-102654.jpg)

## 实验代码

```go
// main.go
package main

import (
	"fmt"
	"github.com/go-redis/redis"
	_ "github.com/go-sql-driver/mysql"
	"github.com/jinzhu/gorm"
	"log"
	"net/http"
	"strconv"
	"time"
)

type Envelope struct {
	Id        int `gorm:"primary_key"`
	Code      string
	UserId    int
	CreatedAt time.Time
	RewardAt  *time.Time
}

func (Envelope) TableName() string {
	return "envelope"
}

func (p *Envelope) BeforeCreate() error {
	p.CreatedAt = time.Now()
	return nil
}

const (
	QueueEnvelope = "envelope"
	QueueUser     = "user"
)

var (
	db          *gorm.DB
	redisClient *redis.Client
)

func init() {
	var err error
	db, err = gorm.Open("mysql", "root:root@tcp(localhost:3306)/test?charset=utf8&parseTime=True&loc=Local")
	if err != nil {
		log.Fatal(err)
	}
	if err = db.DB().Ping(); err != nil {
		log.Fatal(err)
	}
	db.DB().SetMaxOpenConns(100)
	fmt.Println("database connected. pool size 10")
}

func init() {
	redisClient = redis.NewClient(&redis.Options{
		Addr:     "localhost:6379",
		DB:       0,
		PoolSize: 100,
	})
	if _, err := redisClient.Ping().Result(); err != nil {
		log.Fatal(err)
	}
	fmt.Println("redis connected. pool size 100")
}

// 读取Code写入Queue
func init() {
	envelopes := make([]Envelope, 0, 100)
	if err := db.Debug().Where("user_id=0").Limit(100).Find(&envelopes).Error; err != nil {
		log.Fatal(err)
	}
	if len(envelopes) != 100 {
		log.Fatal("不足100个奖品")
	}
	for i := range envelopes {
		if err := redisClient.LPush(QueueEnvelope, envelopes[i].Code).Err(); err != nil {
			log.Fatal(err)
		}
	}
	fmt.Println("load 100 envelopes")
}

func main() {
	http.HandleFunc("/envelope", func(w http.ResponseWriter, r *http.Request) {
		uid := r.Header.Get("x-user-id")
		if uid == "" {
			w.WriteHeader(401)
			_, _ = fmt.Fprint(w, "UnAuthorized")
			return
		}
		uidValue, err := strconv.Atoi(uid)
		if err != nil {
			w.WriteHeader(400)
			_, _ = fmt.Fprint(w, "Bad Request")
			return
		}
		// 检测用户是否抢过了
		if result, err := redisClient.HIncrBy(QueueUser, uid, 1).Result(); err != nil || result != 1 {
			w.WriteHeader(429)
			_, _ = fmt.Fprint(w, "Too Many Request")
			return
		}
		// 检测是否在队列中
		code, err := redisClient.LPop(QueueEnvelope).Result()
		if err != nil {
			w.WriteHeader(200)
			_, _ = fmt.Fprint(w, "No Envelope")
			return
		}
		// 发放红包
		envelope := &Envelope{}
		err = db.Where("code=?", code).Take(&envelope).Error
		if err == gorm.ErrRecordNotFound {
			w.WriteHeader(200)
			_, _ = fmt.Fprint(w, "No Envelope")
			return
		}
		if err != nil {
			w.WriteHeader(500)
			_, _ = fmt.Fprint(w, err)
			return
		}
		now := time.Now()
		envelope.UserId = uidValue
		envelope.RewardAt = &now
		rowsAffected := db.Where("user_id=0").Save(&envelope).RowsAffected // 添加user_id=0来验证Redis是否真的解决争抢问题
		if rowsAffected == 0 {
			fmt.Printf("发生争抢. id=%d\n", envelope.Id)
			w.WriteHeader(500)
			_, _ = fmt.Fprintf(w, "发生争抢. id=%d\n", envelope.Id)
			return
		}
		_, _ = fmt.Fprint(w, envelope.Code)
	})

	fmt.Println("listen on 8080")
	fmt.Println(http.ListenAndServe(":8080", nil))
}
```

