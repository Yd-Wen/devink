"""初始化数据库：读取 env 配置，生成 init.sql"""

import argparse
import hashlib
import sys
from pathlib import Path

# 项目根目录（sql/ 的父目录）
ROOT_DIR = Path(__file__).resolve().parent.parent
BACKEND_ENV = ROOT_DIR / "backend" / ".env"
TEMPLATE_FILE = ROOT_DIR / "sql" / "init.sql.template"
OUTPUT_FILE = ROOT_DIR / "sql" / "init.sql"


def load_env(env_path: Path) -> dict[str, str]:
    """加载 .env 文件"""
    if not env_path.exists():
        print(f"错误: .env 文件不存在: {env_path}", file=sys.stderr)
        sys.exit(1)

    try:
        from dotenv import dotenv_values
        return dotenv_values(str(env_path))
    except ImportError:
        pass

    # 手动解析（兜底）
    env = {}
    with open(env_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            env[key.strip()] = value.strip().strip("\"'")
    return env


def compute_hash(password: str, salt: str) -> str:
    """MD5(password + salt)"""
    return hashlib.md5((password + salt).encode()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description="生成 init.sql（从 env 配置读取密码）")
    parser.add_argument("--execute", action="store_true", help="生成后直接执行 SQL")
    args = parser.parse_args()

    env = load_env(BACKEND_ENV)

    password_salt = env.get("PASSWORD_SALT")
    init_admin_password = env.get("INIT_ADMIN_PASSWORD")

    if not password_salt:
        print("错误: .env 中未配置 PASSWORD_SALT", file=sys.stderr)
        sys.exit(1)
    if not init_admin_password:
        print("错误: .env 中未配置 INIT_ADMIN_PASSWORD", file=sys.stderr)
        sys.exit(1)

    password_hash = compute_hash(init_admin_password, password_salt)

    if not TEMPLATE_FILE.exists():
        print(f"错误: 模板文件不存在: {TEMPLATE_FILE}", file=sys.stderr)
        sys.exit(1)

    content = TEMPLATE_FILE.read_text(encoding="utf-8")

    if "{{INIT_PASSWORD_HASH}}" not in content:
        print("错误: 模板中未找到占位符 {{INIT_PASSWORD_HASH}}", file=sys.stderr)
        sys.exit(1)

    content = content.replace("{{INIT_PASSWORD_HASH}}", password_hash)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(content, encoding="utf-8")

    print(f"[OK] init.sql 已生成: {OUTPUT_FILE}")
    print(f"      用户: admin / user / test")
    print(f"      密码: {init_admin_password}")
    print(f"      哈希: {password_hash}")

    if args.execute:
        _execute_sql(content)


def _execute_sql(sql: str):
    """直接执行 SQL（需 PyMySQL）"""
    try:
        import pymysql
    except ImportError:
        print("错误: --execute 需要 pymysql，请先安装", file=sys.stderr)
        sys.exit(1)

    env = load_env(BACKEND_ENV)

    host = env.get("DB_HOST", "localhost")
    port = int(env.get("DB_PORT", 3306))
    user = env.get("DB_USER", "root")
    password = env.get("DB_PASSWORD", "")
    database = env.get("DB_NAME", "devink")

    conn = pymysql.connect(host=host, port=port, user=user, password=password)
    try:
        with conn.cursor() as cursor:
            for statement in sql.split(";"):
                stmt = statement.strip()
                if stmt:
                    cursor.execute(stmt)
        conn.commit()
        print(f"[OK] SQL 已成功执行到 {host}:{port}/{database}")
    except Exception as e:
        print(f"错误: SQL 执行失败: {e}", file=sys.stderr)
        conn.rollback()
        sys.exit(1)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
