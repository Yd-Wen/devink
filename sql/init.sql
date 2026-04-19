-- 创建库
CREATE DATABASE IF NOT EXISTS devink CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE devink;

-- 用户表
-- userAccount 唯一键可利用数据库天然防重
-- userName 索引提高按昵称查询效率
-- editTime 用户编辑个人资料时间，业务代码主动更新
-- updateTime 用户任何字段更新的时间，on update CURRENT_TIMESTAMP 数据库自动维护
CREATE TABLE IF NOT EXISTS user
(
    id                  bigint auto_increment comment 'id' primary key,
    userAccount         varchar(256)                                not null comment '账号',
    userPassword        varchar(512)                                not null comment '密码',
    userName            varchar(256)                                null comment '用户昵称',
    userAvatar          varchar(1024)                               null comment '用户头像',
    userDescription     varchar(512)                                null comment '用户简介',
    userRole            varchar(256)    default 'user'              not null comment '用户角色：user/admin',
    editTime            datetime        default CURRENT_TIMESTAMP   not null comment '编辑时间',
    createTime          datetime        default CURRENT_TIMESTAMP   not null comment '创建时间',
    updateTime          datetime        default CURRENT_TIMESTAMP   not null on update CURRENT_TIMESTAMP comment '更新时间',
    isDelete            tinyint         default 0                   not null comment '是否删除',
    UNIQUE KEY uk_userAccount (userAccount),
    INDEX idx_userName (userName)
) comment '用户' collate = utf8mb4_unicode_ci;

-- 初始化测试数据（密码是 12345678，MD5 加密 + 盐值 ）
INSERT INTO user (id, userAccount, userPassword, userName, userAvatar, userDescription, userRole) VALUES
(1, 'admin', '10670d38ec32fa8102be6a37f8cb52bf', '管理员', 'https://www.codefather.cn/logo.png', '系统管理员', 'admin'),
(2, 'user', '10670d38ec32fa8102be6a37f8cb52bf', '普通用户', 'https://www.codefather.cn/logo.png', '我是一个普通用户', 'user'),
(3, 'test', '10670d38ec32fa8102be6a37f8cb52bf', '测试账号', 'https://www.codefather.cn/logo.png', '这是一个测试账号', 'user');

-- 文章表
create table if not exists blog
(
    id              bigint auto_increment comment 'id' primary key,
    taskId          varchar(64)                        not null comment '任务ID（UUID）',
    userId          bigint                             not null comment '用户ID',
    topic           varchar(500)                       not null comment '选题',
    style           varchar(20)                        null comment '博客风格：tech/emotional/educational/humorous',
    mainTitle       varchar(200)                       null comment '主标题',
    subTitle        varchar(300)                       null comment '副标题',
    outline         json                               null comment '大纲（JSON格式）',
    content         text                               null comment '正文（Markdown格式）',
    fullContent     text                               null comment '完整图文（Markdown格式，含配图）',
    coverImage      varchar(512)                       null comment '封面图 URL',
    images          json                               null comment '配图列表（JSON数组）',
    phase           varchar(50)    default 'PENDING'   null comment '当前阶段：PENDING/TITLE_GENERATING/TITLE_SELECTING/OUTLINE_GENERATING/OUTLINE_EDITING/CONTENT_GENERATING',
    titleOptions    json                               null comment '标题方案列表（3-5个方案）',
    userDescription text                               null comment '用户补充描述',
    enabledImageMethods json                           null comment '允许的配图方式列表',
    status          varchar(20) default 'PENDING'      not null comment '状态：PENDING/PROCESSING/COMPLETED/FAILED',
    errorMessage    text                               null comment '错误信息',
    createTime      datetime    default CURRENT_TIMESTAMP not null comment '创建时间',
    completedTime   datetime                           null comment '完成时间',
    updateTime      datetime    default CURRENT_TIMESTAMP not null on update CURRENT_TIMESTAMP comment '更新时间',
    isDelete        tinyint     default 0              not null comment '是否删除',
    UNIQUE KEY uk_taskId (taskId),
    INDEX idx_userId (userId),
    INDEX idx_status (status),
    INDEX idx_createTime (createTime),
    INDEX idx_userId_status (userId, status)
) comment '博客表' collate = utf8mb4_unicode_ci;

-- 智能体执行日志表
create table if not exists agent_log
(
    id              bigint auto_increment comment 'id' primary key,
    taskId          varchar(64)                        not null comment '任务ID',
    agentName       varchar(50)                        not null comment '智能体名称',
    startTime       datetime                           not null comment '开始时间',
    endTime         datetime                           null comment '结束时间',
    durationMs      int                                null comment '耗时（毫秒）',
    status          varchar(20)                        not null comment '状态：SUCCESS/FAILED',
    errorMessage    text                               null comment '错误信息',
    prompt          text                               null comment '使用的Prompt',
    inputData       json                               null comment '输入数据（JSON格式）',
    outputData      json                               null comment '输出数据（JSON格式）',
    createTime      datetime    default CURRENT_TIMESTAMP not null comment '创建时间',
    updateTime      datetime    default CURRENT_TIMESTAMP not null on update CURRENT_TIMESTAMP comment '更新时间',
    isDelete        tinyint     default 0              not null comment '是否删除',
    INDEX idx_taskId (taskId),
    INDEX idx_agentName (agentName),
    INDEX idx_status (status),
    INDEX idx_createTime (createTime)
) comment '智能体执行日志表' collate = utf8mb4_unicode_ci;