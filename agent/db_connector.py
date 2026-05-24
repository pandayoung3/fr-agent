"""
FR 数据库连接模块
功能：
1. 从 FineReport config_entity.properties 读取连接元数据（host/port/db/user/driver）
2. 从 SQL 文本中提取表名
3. 连接数据库，查询字段结构（information_schema）
4. 将真实字段信息回填到 parsed 数据集中

支持的数据库驱动：
- MySQL / MariaDB（com.mysql.jdbc.Driver, com.mysql.cj.jdbc.Driver）
- 其他驱动（Oracle, SQL Server 等）预留接口，当前返回空结果并提示
"""
import re
import os
from typing import Optional


# ── 1. 从 FR 配置文件读取连接元数据 ─────────────────────────────────────────

def parse_fr_connections(fr_webinf_dir: str) -> dict:
    """
    读取 FineReport 的 config_entity.properties，提取所有数据库连接的元数据。
    注意：密码为 RSA 加密存储，此函数不返回密码。

    参数:
        fr_webinf_dir: FineReport WEB-INF 目录路径
                       例如 /Users/xxx/FineReport/webapps/webroot/WEB-INF

    返回:
        {
          "JDBC2": {
            "driver": "com.mysql.jdbc.Driver",
            "url": "jdbc:mysql://localhost:3306/123",
            "username": "root",
            "host": "localhost",
            "port": 3306,
            "database": "123",
            "db_type": "mysql"
          },
          ...
        }
    """
    prop_path = os.path.join(fr_webinf_dir, "embed", "prop", "config_entity.properties")
    if not os.path.exists(prop_path):
        return {}

    raw: dict[str, str] = {}
    with open(prop_path, encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            k, _, v = line.partition("=")
            # properties 文件转义处理
            raw[k.strip()] = v.strip().replace("\\:", ":").replace("\\=", "=")

    # 找出所有连接名
    conn_names: set[str] = set()
    prefix = "ConnectionConfig.connections."
    for key in raw:
        if key.startswith(prefix):
            parts = key[len(prefix):].split(".")
            if parts:
                conn_names.add(parts[0])

    result = {}
    for name in conn_names:
        base = f"{prefix}{name}."
        driver = raw.get(f"{base}driver", "")
        url = raw.get(f"{base}url", "")
        username = raw.get(f"{base}authentication.username", "")

        host, port, database = _parse_jdbc_url(url)
        db_type = _detect_db_type(driver, url)

        result[name] = {
            "driver": driver,
            "url": url,
            "username": username,
            "host": host,
            "port": port,
            "database": database,
            "db_type": db_type,
        }

    return result


def _parse_jdbc_url(url: str) -> tuple:
    """从 JDBC URL 提取 host、port、database"""
    # jdbc:mysql://host:port/database
    m = re.search(r"//([^/:]+)(?::(\d+))?/([^?&\s]+)", url)
    if m:
        host = m.group(1)
        port = int(m.group(2)) if m.group(2) else _default_port(url)
        database = m.group(3).split("?")[0]
        return host, port, database
    # jdbc:sqlite://path  或  ${ENV_HOME}/...  等特殊形式
    return "localhost", 0, ""


def _default_port(url: str) -> int:
    url_lower = url.lower()
    if "mysql" in url_lower:
        return 3306
    if "oracle" in url_lower:
        return 1521
    if "sqlserver" in url_lower or "mssql" in url_lower:
        return 1433
    if "postgresql" in url_lower:
        return 5432
    return 0


def _detect_db_type(driver: str, url: str) -> str:
    text = (driver + url).lower()
    if "mysql" in text or "mariadb" in text:
        return "mysql"
    if "oracle" in text:
        return "oracle"
    if "sqlserver" in text or "mssql" in text:
        return "sqlserver"
    if "postgresql" in text or "postgres" in text:
        return "postgresql"
    if "sqlite" in text:
        return "sqlite"
    return "unknown"


# ── 2. 从 SQL 中提取表名 ─────────────────────────────────────────────────────

def extract_table_names(sql: str) -> list:
    """
    从 SQL 文本中提取表名（支持 FROM / JOIN / UPDATE / INTO）。
    忽略子查询括号内的 FROM、CTE 名称和 SQL 关键字。
    """
    if not sql:
        return []

    # 去掉注释
    sql_clean = re.sub(r"--[^\n]*", " ", sql)
    sql_clean = re.sub(r"/\*.*?\*/", " ", sql_clean, flags=re.DOTALL)

    # 匹配 FROM / JOIN / UPDATE / INTO 后面的表名（可带 schema 前缀）
    pattern = r"(?:FROM|JOIN|UPDATE|INTO)\s+([\w.`\[\]\"]+)"
    matches = re.findall(pattern, sql_clean, re.IGNORECASE)

    # 清理：去掉反引号、引号、schema 前缀保留表名部分
    tables = []
    sql_keywords = {
        "select", "where", "and", "or", "on", "set", "values",
        "inner", "left", "right", "outer", "cross", "full",
        "group", "order", "having", "limit", "union", "all",
    }
    for t in matches:
        t = t.strip("`[]\"'")
        # 如果有 schema.table，只取 table 部分
        if "." in t:
            t = t.split(".")[-1]
        if t.lower() not in sql_keywords and t:
            tables.append(t)

    return list(dict.fromkeys(tables))  # 去重保序


# ── 3. 连接数据库获取字段结构 ────────────────────────────────────────────────

def fetch_schema(conn_meta: dict, password: str, tables: list) -> dict:
    """
    连接数据库，查询指定表的字段结构。

    返回:
        {
          "CourseGrade": [
            {"column": "id",        "type": "varchar(20)", "comment": "", "key": "PRI"},
            {"column": "studentno", "type": "varchar(20)", "comment": "", "key": "MUL"},
            ...
          ],
          ...
        }
    失败时返回空字典，不抛异常（让调用方决定是否展示错误）。
    """
    db_type = conn_meta.get("db_type", "unknown")

    if db_type == "mysql":
        return _fetch_mysql_schema(conn_meta, password, tables)
    else:
        # 其他数据库类型预留接口
        print(f"[DB] 暂不支持 db_type={db_type}，跳过字段获取")
        return {}


def _fetch_mysql_schema(conn_meta: dict, password: str, tables: list) -> dict:
    try:
        import pymysql
    except ImportError:
        print("[DB] pymysql 未安装，无法连接 MySQL")
        return {}

    host = conn_meta.get("host", "localhost")
    port = conn_meta.get("port", 3306) or 3306
    database = conn_meta.get("database", "")
    username = conn_meta.get("username", "root")

    try:
        conn = pymysql.connect(
            host=host, port=int(port),
            user=username, password=password,
            database=database,
            connect_timeout=8,
            charset="utf8mb4",
        )
    except Exception as e:
        print(f"[DB] MySQL 连接失败: {e}")
        raise

    result = {}
    try:
        with conn.cursor() as cur:
            if not tables:
                return {}

            placeholders = ",".join(["%s"] * len(tables))
            cur.execute(f"""
                SELECT TABLE_NAME, COLUMN_NAME, COLUMN_TYPE, COLUMN_COMMENT, COLUMN_KEY
                FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = %s
                  AND TABLE_NAME IN ({placeholders})
                ORDER BY TABLE_NAME, ORDINAL_POSITION
            """, [database] + [t for t in tables])

            for table_name, col_name, col_type, col_comment, col_key in cur.fetchall():
                if table_name not in result:
                    result[table_name] = []
                result[table_name].append({
                    "column": col_name,
                    "type": col_type,
                    "comment": col_comment or "",
                    "key": col_key or "",
                })
    finally:
        conn.close()

    return result


# ── 4. 将真实字段信息回填到 parsed 数据集 ────────────────────────────────────

def enrich_parsed_datasets(parsed: dict, conn_meta_map: dict, passwords: dict) -> tuple:
    """
    主入口：对 parsed 中所有 DBTableData 数据集，查询字段结构并回填。

    参数:
        parsed:        summarize_to_dict() 返回的解析结果
        conn_meta_map: parse_fr_connections() 返回的连接元数据
        passwords:     {连接名: 密码}，例如 {"JDBC2": "xxx"}

    返回:
        (enriched_parsed, report)
        enriched_parsed: 已回填字段的 parsed 副本
        report: {
            "success": ["JDBC2/CourseGrade", ...],
            "failed":  [{"conn": "JDBC2", "error": "..."}],
            "skipped": ["FRDemo"],   # 不在 passwords 里的连接
        }
    """
    import copy
    result = copy.deepcopy(parsed)
    report = {"success": [], "failed": [], "skipped": []}

    # 按连接分组需要查询的表
    conn_tables: dict[str, set] = {}
    ds_conn_map = {}  # dataset_name → conn_name
    for ds in result.get("datasets", []):
        if ds.get("type") != "DBTableData":
            continue
        conn_name = ds.get("db_connection", "")
        if not conn_name:
            continue
        tables = extract_table_names(ds.get("sql", ""))
        if not tables:
            continue
        if conn_name not in conn_tables:
            conn_tables[conn_name] = set()
        conn_tables[conn_name].update(tables)
        ds_conn_map[ds["name"]] = (conn_name, tables)

    # 按连接查询 schema
    schema_cache: dict[str, dict] = {}  # conn_name → schema
    for conn_name, tables in conn_tables.items():
        if conn_name not in passwords:
            report["skipped"].append(conn_name)
            continue
        meta = conn_meta_map.get(conn_name)
        if not meta:
            report["failed"].append({"conn": conn_name, "error": "未找到连接配置"})
            continue
        try:
            schema = fetch_schema(meta, passwords[conn_name], list(tables))
            schema_cache[conn_name] = schema
            for t in tables:
                if t in schema:
                    report["success"].append(f"{conn_name}/{t}")
        except Exception as e:
            report["failed"].append({"conn": conn_name, "error": str(e)})

    # 回填到数据集
    for ds in result.get("datasets", []):
        if ds["name"] not in ds_conn_map:
            continue
        conn_name, tables = ds_conn_map[ds["name"]]
        schema = schema_cache.get(conn_name, {})

        # 合并所有涉及表的字段
        all_columns = []
        seen = set()
        for t in tables:
            for col_info in schema.get(t, []):
                col = col_info["column"]
                if col not in seen:
                    seen.add(col)
                    all_columns.append(col)

        if all_columns:
            ds["columns"] = all_columns
            # 额外存一份带类型和注释的完整结构，供 LLM 用
            ds["column_details"] = {
                t: schema.get(t, []) for t in tables if t in schema
            }

    return result, report
