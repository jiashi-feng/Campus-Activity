# 校园活动管理系统

## 项目简介

校园活动管理系统是一个基于Flask的Web应用，旨在帮助高校管理校园活动的全生命周期。系统支持多种角色（学生、组织者、管理员、教师）分别管理活动的创建、审批、报名、资金申请等流程，提高校园活动的组织效率和管理透明度。

## 功能特点

### 多角色支持
- **学生**：浏览活动、报名参加、查看个人活动记录
- **组织者**：创建活动、管理活动详情、查看报名情况
- **管理员**：审批活动申请、管理系统设置
- **教师**：审批资金申请、评估活动成果

### 核心功能
- 活动创建与管理
- 活动审批流程
- 学生报名系统
- 资金申请与审批
- 场地预约管理
- 活动评分与反馈

## 技术栈

- **后端**：Python Flask
- **数据库**：SQLite
- **前端**：HTML, CSS, JavaScript, Bootstrap 5
- **模板引擎**：Jinja2

## 安装指南

### 环境要求
- Python 3.6+
- Flask

### 安装步骤

1. 克隆仓库到本地
```bash
git clone https://github.com/yourusername/Campus-Activity.git
cd Campus-Activity
```

2. 安装依赖
```bash
pip install flask
``` 

3. 初始化数据库
```bash
python init_db.py
```

4. 运行应用
```bash
python app.py
```
5. 访问应用 
在浏览器中访问
http://localhost:5000

## 系统角色与账号
系统预设了以下测试账号（用户名/密码）：
| 用户名     | 密码   | 角色     | 真实姓名     |
|------------|--------|----------|--------------|
| admin      | 123456 | 管理员   | 系统管理员   |
| teacher1   | 123456 | 教师     | 张老师       |
| organizer1 | 123456 | 组织者   | 李组织者     |
| student1   | 123456 | 学生     | 王学生       |
| student2   | 123456 | 学生     | 赵同学       |


## 使用指南
### 学生用户
1. 登录系统
2. 浏览可报名活动列表
3. 报名参加感兴趣的活动
4. 查看个人活动参与记录
### 组织者
1. 登录系统
2. 创建新活动（填写活动详情、场地、时间等信息）
3. 管理已创建的活动
4. 查看活动报名情况
### 管理员
1. 登录系统
2. 审批待审核的活动申请
3. 查看活动统计数据
### 教师
1. 登录系统
2. 审批资金申请
3. 为已完成的活动评分


## 项目结构
```plaintext
Campus-Activity/
├── app.py                 # 主应用文件，包含路由和业务逻辑
├── init_db.py             # 数据库初始化脚本
├── campus.db              # SQLite数据库文件
├── static/                # 静态资源目录
│   ├── css/               # CSS样式文件
│   ├── js/                # JavaScript文件
│   └── images/            # 图片资源
└── templates/             # HTML模板目录
    ├── admin/             # 管理员相关页面
    ├── organizer/         # 组织者相关页面
    ├── student/           # 学生相关页面
    ├── teacher/           # 教师相关页面
    ├── base.html          # 基础模板
    └── login.html         # 登录页面
 ```

## 数据库设计
系统使用SQLite数据库，主要包含以下表：

- Users ：用户信息表，存储不同角色用户的账号信息
- Activities ：活动信息表，存储活动的基本信息
- Places ：场地信息表，存储可用于活动的场地信息
- Participations ：参与记录表，记录学生参与活动的情况
- Funds ：资金记录表，记录活动的资金申请和审批情况
## 开发与贡献
欢迎贡献代码或提出建议，请遵循以下步骤：

1. Fork 本仓库
2. 创建您的特性分支 ( git checkout -b feature/amazing-feature )
3. 提交您的更改 ( git commit -m 'Add some amazing feature' )
4. 推送到分支 ( git push origin feature/amazing-feature )
5. 打开一个 Pull Request

## 许可证
本项目采用 MIT 许可证 - 详情请参见 LICENSE 文件

## 联系方式
- 项目维护者：[jiashi]
- 项目链接：[https://github.com/jiashi-feng/Campus-Activity]