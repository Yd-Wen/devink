use devink;

-- 为 blog 表添加 style 字段（文章风格）
ALTER TABLE blog
    ADD COLUMN style VARCHAR(20) NULL COMMENT '博客风格：tech/emotional/educational/humorous' AFTER topic;