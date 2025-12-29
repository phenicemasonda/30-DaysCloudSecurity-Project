import json
import boto3
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def get_db_engine():
    client = boto3.client("secretsmanager")
    secret = client.get_secret_value(
        SecretId="arn:aws:secretsmanager:af-south-1:839754490065:secret:rds!db-b9cccd63-5f34-4f53-851a-6d3396b43cba-YqPOyo"
    )
    creds = json.loads(secret["SecretString"])

    # Add host, port, dbname manually
    host = "verdant-db.c1kk4kq2iix3.af-south-1.rds.amazonaws.com"
    port = 5432
    dbname = "verdant-db"

    db_url = (
        f"postgresql://{creds['username']}:{creds['password']}"
        f"@{host}:{port}/{dbname}"
    )

    return create_engine(db_url, pool_pre_ping=True)

engine = get_db_engine()
SessionLocal = sessionmaker(bind=engine)

from utils.security import encrypt_log

def insert_auth_log(cur, email, ip, user_agent, status, timestamp):
    cur.execute(
        """
        INSERT INTO auth_activity_logs (user_email, auth_method, ip_address, user_agent, status, timestamp)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (encrypt_log(email), 'SAML', encrypt_log(ip), encrypt_log(user_agent), status, timestamp)
    )
from utils.security import decrypt_log

def fetch_auth_logs(cur):
    """
    Fetch and decrypt authentication activity logs.
    Decrypts user_email, ip_address, and user_agent columns.
    """
    cur.execute("""
        SELECT user_email, auth_method, ip_address, user_agent, status, timestamp
        FROM auth_activity_logs
    """)
    rows = cur.fetchall()

    decrypted_logs = []
    for row in rows:
        decrypted_logs.append((
            decrypt_log(row[0]),   # user_email
            row[1],                # auth_method (not encrypted)
            decrypt_log(row[2]),   # ip_address
            decrypt_log(row[3]),   # user_agent
            row[4],                # status (not encrypted)
            row[5]                 # timestamp (not encrypted)
        ))

    return decrypted_logs
