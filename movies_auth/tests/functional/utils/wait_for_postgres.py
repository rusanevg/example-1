import psycopg2

from backoff import backoff


try:
    from settings import test_settings
except ImportError:
    import sys
    sys.path.append(sys.path[0] + '/..')
    from settings import test_settings


@backoff()
def check_postgres():
    conn = psycopg2.connect(
        host=test_settings.DB_HOST,
        dbname=test_settings.DB_NAME,
        user=test_settings.DB_USER,
        password=test_settings.DB_PASSWORD,
        connect_timeout=1,
    )
    conn.close()


if __name__ == "__main__":
    check_postgres()
