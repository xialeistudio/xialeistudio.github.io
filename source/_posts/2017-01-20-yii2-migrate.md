---
title: Yii2 migrate使用
layout: post
categories:
- Engineering
tags:
- yii
---
试想一个很简单的场景，在使用Yii2开发时，如果对已经有数据的数据表结构进行编辑的话，需要同步数据结构需要在本地导出一份SQL，放到线上去执行SQL，非常的不方便。
而有了Yii2 migrate工具之后，这个问题简直不是问题。以下对常用的表结构操作进行演示。
## 关键命令

+ 创建migrate
```
yii migrate/create [名称]
```
+ 执行migrate升级
```
yii migrate
```
+ 执行migrate降级
```
yii migrate/down
```

## 创建新表
执行创建migrate命令后，项目文件夹下migrations中会多出**m170119_093917_[名称].php**的文件，文件名称可能不同，但是结构是相同的，打开该php文件，内容如下

```php
<?php
use yii\db\Migration;

class m170119_093917_name_20 extends Migration
{
	public function up()
	{
		$tableName = 't_category';
		$this->createTable($tableName, [
			'id' => $this->primaryKey(),
			'name' => $this->string(10)->notNull()->unique()->comment('标识'),
			'title' => $this->string(6)->notNull()->comment('名称'),
			'count' => $this->integer()->defaultValue(0)->notNull()->comment('入驻数量')
		]);
	}

	public function down()
	{
		echo "m170119_093917_name_20 cannot be reverted.\n";
		return false;
	}

	/*
	// Use safeUp/safeDown to run migration code within a transaction
	public function safeUp()
	{
	}

	public function safeDown()
	{
	}
	*/
}
```

如果需要支持降级的话在**down**方法中写逻辑返回true即可。

*以下代码演示Migration操作，不再新建migrate，执行使用本php文件即可*
## 添加字段

```php
<?php
$this->addColumn('t_category','sort',$this->integer()->defaultValue(0)->notNull()->comment('排序'));
```

## 添加索引

```php
<?php
$this->createIndex('sort','t_category',['sort']);
```

## 添加唯一索引

```php
<?php
$this->createIndex('sort','t_category',['sort'],true);
```

## 更新字段

```php
<?php
$this->alterColumn('t_category','sort',$this->smallInteger()->defaultValue(0)->notNull()->comment('排序'));
```

## 删除字段

```php
<?php
$this->dropColumn('t_category','sort');
```

## 删除表

```php
<?php
$this->dropTable('t_category');
```