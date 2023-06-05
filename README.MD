
## 运行

 修改`djangoblog/setting.py` 修改数据库配置，如下所示：

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'djangoblog',
        'USER': 'root',
        'PASSWORD': 'password',
        'HOST': 'host',
        'PORT': 3306,
    }
}
```

### 创建数据库
mysql数据库中执行:
```sql
CREATE DATABASE djangoblog;
```

终端下执行:
```bash
python manage.py makemigrations
python manage.py migrate
```

### 创建超级用户
 终端下执行:
```bash
python manage.py createsuperuser
```


### 开始运行：
 终端下执行:
```bash
python manage.py runserver
```

浏览器打开: http://127.0.0.1:8000/   


用户表 (user)
- user_id       (int, primary key)                 用户id
- username      (varchar(50), not null)            用户名
- email         (varchar(100), not null)           邮箱
- password      (varchar(100), not null)           密码（加密后）
- avatar        (varchar(255))                     用户头像地址
- nickname      (varchar(50))                      用户昵称
- gender        (enum('male', 'female', 'secret')) 用户性别
- birthday      (date)                             用户生日 
- location      (varchar(100))                     用户所在地区
- introduction  (text)                             用户简介
- website       (varchar(255))                     用户个人网站地址
- social_links  (text)                             用户社交媒体链接（可以包含多个）
- registered_at (datetime)                         用户注册时间
- last_login_at (datetime)                         最后一次登录时间
```sql
CREATE TABLE user (
    user_id INT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL,
    password VARCHAR(100) NOT NULL,
    avatar VARCHAR(255),
    nickname VARCHAR(50),
    gender ENUM('male', 'female', 'secret'),
    birthday DATE,
    location VARCHAR(100),
    introduction TEXT,
    website VARCHAR(255),
    social_links TEXT,
    registered_at DATETIME,
    last_login_at DATETIME
);
```

分类表 (category)
- category_id  (int, primary key)                                  分类主键 id
- name         (varchar(50), not null)                             分类名称
- description  (text)                                              分类描述，对此分类进行详细解释说明
- parent_id    (int, foreign key references category(category_id)) 父级分类 ID，用于自关联，参照本表中另一条记录的 id 字段。
- created_at   (datetime)                                          该分类创建时间戳
- updated_at   (datetime)                                          该分类的更新时间戳 
```sql
CREATE TABLE category (
    category_id INT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    parent_id INT REFERENCES category(id),
    created_at DATETIME,
    updated_at DATETIME
);
```

文章表 (post)
- post_id          (int, primary key)                       文章id
- user_id          (int, foreign key)                       作者id
- category_id      (int, foreign key)                       文章分类id
- title            (varchar(255), not null)                 标题
- content          (text, not null)                         内容
- image_url        (varchar(255))                           配图地址
- published_at     (datetime)                               发布时间
- views            (int)                                    浏览量
- likes            (int)                                    点赞数
- dislikes         (int)                                    点踩数
- is_public        (boolean)                                是否公开
- status           (enum('draft', 'published', 'archived')) 文章状态
- meta_keywords    (text)                                   文章的meta keywords标签（用于SEO优化）
- meta_description (text)                                   文章的meta description标签（用于SEO优化）
- updated_at       (datetime)                               文章更新时间

```sql
CREATE TABLE post (
    post_id INT PRIMARY KEY,
    user_id INT,
    category_id INT,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    image_url VARCHAR(255),
    published_at DATETIME,
    views INT,
    likes INT,
    dislikes INT,
    is_public BOOLEAN,
    status ENUM('draft', 'published', 'archived'),
    meta_keywords TEXT,
    meta_description TEXT,
    updated_at DATETIME
);
```

评论表 (comment)
- comment_id   (int, primary key)                        评论id
- user_id      (int, foreign key)                        评论者id
- post_id      (int, foreign key)                        所评论文章的id
- parent_id    (int, foreign key)                        父级评论ID（如果是回复某条评论，需要填充这个字段）
- root_id      (int, foreign key)                        "根"评论ID（方便查找所有层级子集）
- content      (text)                                    内容 
- created_at   (datetime)                                评论时间 
- likes        (int)                                     点赞数 
- dislikes     (int)                                     点踩数
- status       (enum('approved', 'rejected', 'pending')) 评论状态（已审核，已拒绝，待审核）
- is_top       (boolean)                                 是否置顶
- email        (varchar(100))                            评论者邮箱地址
- updated_at   (datetime)                                评论更新时间
```sql
CREATE TABLE comment (
  comment_id INT PRIMARY KEY,
  user_id INT,
  post_id INT,
  parent_id INT,
  root_id INT,
  content TEXT,
  created_at DATETIME,
  likes INT,
  dislikes INT,
  status ENUM('approved', 'rejected', 'pending'),
  is_top BOOLEAN,
  email VARCHAR(100),
  updated_at DATETIME,
  FOREIGN KEY (user_id) REFERENCES user(user_id),
  FOREIGN KEY (post_id) REFERENCES article(post_id)
);
```

访问日志表(accesslog)
- access_id  (int, primary key)          访问记录id
- user_id    (int, foreign key nullable) 用户id，如果未登录，则该字段为NULL
- post_id    (int, foreign key nullable) 被访问的文章id，如果是浏览分类页面则该字段为NULL
- ip_address (varchar(100))              访问来源IP地址（完整格式）
- platform   (varchar(50))               访问所使用设备/平台（如Windows、Android等）
- browser    (varchar(255))              使用的浏览器类型及版本号
- created_at (datetime)                  记录创建时间戳
```sql
CREATE TABLE `accesslog` (
  `access_id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11),
  `post_id` int(11),
  `ip_address` varchar(100) NOT NULL,
  `platform` varchar(50) DEFAULT NULL,
  `browser` varchar(255) DEFAULT NULL,
  `created_at` datetime NOT NULL,
  PRIMARY KEY (`access_id`),
  FOREIGN KEY (`user_id`) REFERENCES `users`(`user_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (`post_id`) REFERENCES `posts`(`post_id`) ON DELETE CASCADE ON UPDATE CASCADE
);
```