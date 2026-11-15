
import sqlite3
import os
import pandas as pd

DB_PATH = os.path.join(
    os.path.dirname(__file__),
    "data",
    "astroguard.db"
)


def connect():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return sqlite3.connect(DB_PATH)


def init_db():

    with connect() as con:

        # Astronaut table
        con.execute("""
            CREATE TABLE IF NOT EXISTS astronauts (
                astronaut_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Measurements table
        con.execute("""
            CREATE TABLE IF NOT EXISTS measurements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                measured_at TEXT DEFAULT CURRENT_TIMESTAMP,

                heart_rate REAL NOT NULL,
                temperature REAL NOT NULL,
                oxygen REAL NOT NULL,

                respiratory_rate REAL,
                systolic_bp REAL,
                diastolic_bp REAL,
                radiation_rate REAL,
                radiation_dose REAL,

                note TEXT,
                activity_state TEXT DEFAULT 'rest',
                sleep_hours REAL DEFAULT 0,
                sleep_quality INTEGER DEFAULT 3,
                exercise_minutes INTEGER DEFAULT 0,
                exercise_intensity TEXT DEFAULT 'none',
                fatigue_level INTEGER DEFAULT 1,
                stress_level INTEGER DEFAULT 1,
                symptoms TEXT DEFAULT '',
                astronaut_id TEXT DEFAULT 'AST-001'
            )
        """)

        # Add missing columns to old databases
        existing_columns = {
            row[1]
            for row in con.execute(
                "PRAGMA table_info(measurements)"
            ).fetchall()
        }

        new_columns = {
            "activity_state": "TEXT DEFAULT 'rest'",
            "sleep_hours": "REAL DEFAULT 0",
            "sleep_quality": "INTEGER DEFAULT 3",
            "exercise_minutes": "INTEGER DEFAULT 0",
            "exercise_intensity": "TEXT DEFAULT 'none'",
            "fatigue_level": "INTEGER DEFAULT 1",
            "stress_level": "INTEGER DEFAULT 1",
            "symptoms": "TEXT DEFAULT ''",
            "astronaut_id": "TEXT DEFAULT 'AST-001'",

            "respiratory_rate": "REAL",
            "systolic_bp": "REAL",
            "diastolic_bp": "REAL",
            "radiation_rate": "REAL",
            "radiation_dose": "REAL"
        }

        for column, definition in new_columns.items():
            if column not in existing_columns:
                con.execute(
                    f"ALTER TABLE measurements "
                    f"ADD COLUMN {column} {definition}"
                )
        # Earth baseline
        con.execute("""
            CREATE TABLE IF NOT EXISTS baseline (
                astronaut_id TEXT PRIMARY KEY,
                heart_rate REAL NOT NULL,
                temperature REAL NOT NULL,
                oxygen REAL NOT NULL,
                respiratory_rate REAL,
                systolic_bp REAL,
                diastolic_bp REAL,
                radiation_rate REAL,
                radiation_dose REAL
            )
        """)

        # Eski baseline tablosunu yeni yapıya taşı
        baseline_columns = {
            row[1]
            for row in con.execute(
                "PRAGMA table_info(baseline)"
            ).fetchall()
        }

        if "astronaut_id" not in baseline_columns:

            con.execute("""
                ALTER TABLE baseline RENAME TO baseline_old
            """)

            con.execute("""
                CREATE TABLE baseline (
                    astronaut_id TEXT PRIMARY KEY,
                    heart_rate REAL NOT NULL,
                    temperature REAL NOT NULL,
                    oxygen REAL NOT NULL,
                    respiratory_rate REAL,
                    systolic_bp REAL,
                    diastolic_bp REAL,
                    radiation_rate REAL,
                    radiation_dose REAL
                )
            """)

            old_data = con.execute("""
                SELECT heart_rate, temperature, oxygen
                FROM baseline_old
                WHERE id = 1
            """).fetchone()

            if old_data:
                con.execute("""
                    INSERT INTO baseline (
                        astronaut_id,
                        heart_rate,
                        temperature,
                        oxygen
                    )
                    VALUES ('AST-001', ?, ?, ?)
                """, old_data)

            con.execute("DROP TABLE baseline_old")

        # AI chat conversations
        con.execute("""
            CREATE TABLE IF NOT EXISTS chat_conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT DEFAULT 'New Chat',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                astronaut_id TEXT DEFAULT 'AST-001'
            )
        """)

        # AI chat messages
        con.execute("""
            CREATE TABLE IF NOT EXISTS chat_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                astronaut_id TEXT DEFAULT 'AST-001'
            )
        """)

        # Check old database columns
        chat_columns = {
            row[1]
            for row in con.execute(
                "PRAGMA table_info(chat_messages)"
            ).fetchall()
        }

        # Add conversation_id if missing
        if "conversation_id" not in chat_columns:

            con.execute("""
                ALTER TABLE chat_messages
                ADD COLUMN conversation_id INTEGER
            """)

        # Find old messages without a conversation
        old_messages = con.execute("""
            SELECT DISTINCT astronaut_id
            FROM chat_messages
            WHERE conversation_id IS NULL
        """).fetchall()

        for (astronaut_id,) in old_messages:

            first_message = con.execute("""
                SELECT content
                FROM chat_messages
                WHERE astronaut_id = ?
                AND role = 'user'
                ORDER BY id ASC
                LIMIT 1
            """, (astronaut_id,)).fetchone()

            title = (
                first_message[0][:40]
                if first_message else "Previous Chat"
            )

            cursor = con.execute("""
                INSERT INTO chat_conversations (title, astronaut_id)
                VALUES (?, ?)
            """, (title, astronaut_id))

            new_conversation_id = cursor.lastrowid

            con.execute("""
                UPDATE chat_messages
                SET conversation_id = ?
                WHERE astronaut_id = ?
                AND conversation_id IS NULL
            """, (new_conversation_id, astronaut_id))
        # Add conversation_id to old databases
        chat_columns = {
            row[1]
            for row in con.execute(
                "PRAGMA table_info(chat_messages)"
            ).fetchall()
        }

        if "conversation_id" not in chat_columns:

            con.execute("""
                ALTER TABLE chat_messages
                ADD COLUMN conversation_id INTEGER
            """)

            astronauts_with_messages = con.execute("""
                SELECT DISTINCT astronaut_id
                FROM chat_messages
                WHERE conversation_id IS NULL
            """).fetchall()

            for (astronaut_id,) in astronauts_with_messages:

                first_message = con.execute("""
                    SELECT content
                    FROM chat_messages
                    WHERE astronaut_id = ?
                    AND role = 'user'
                    ORDER BY id ASC
                    LIMIT 1
                """, (astronaut_id,)).fetchone()

                title = (
                    first_message[0][:40]
                    if first_message else "Previous Chat"
                )

                cursor = con.execute("""
                    INSERT INTO chat_conversations (title, astronaut_id)
                    VALUES (?, ?)
                """, (title, astronaut_id))

                conversation_id = cursor.lastrowid

                con.execute("""
                    UPDATE chat_messages
                    SET conversation_id = ?
                    WHERE astronaut_id = ?
                    AND conversation_id IS NULL
                """, (conversation_id, astronaut_id))

        chat_columns = {
            row[1]
            for row in con.execute(
                "PRAGMA table_info(chat_messages)"
            ).fetchall()
        }

        if "astronaut_id" not in chat_columns:
            con.execute("""
                ALTER TABLE chat_messages
                ADD COLUMN astronaut_id TEXT DEFAULT 'AST-001'
            """)


def add_measurement(
    heart_rate,
    temperature,
    oxygen,
    note="",
    activity_state="rest",
    sleep_hours=0,
    sleep_quality=3,
    exercise_minutes=0,
    exercise_intensity="none",
    fatigue_level=1,
    stress_level=1,
    symptoms="",
    astronaut_id="AST-001",
    respiratory_rate=None,
    systolic_bp=None,
    diastolic_bp=None,
    radiation_rate=None,
    radiation_dose=None
):

    with connect() as con:

        con.execute("""
            INSERT INTO measurements (
                heart_rate,
                temperature,
                oxygen,
                respiratory_rate,
                systolic_bp,
                diastolic_bp,
                radiation_rate,
                radiation_dose,
                note,
                activity_state,
                sleep_hours,
                sleep_quality,
                exercise_minutes,
                exercise_intensity,
                fatigue_level,
                stress_level,
                symptoms,
                astronaut_id
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            heart_rate,
            temperature,
            oxygen,
            respiratory_rate,
            systolic_bp,
            diastolic_bp,
            radiation_rate,
            radiation_dose,
            note,
            activity_state,
            sleep_hours,
            sleep_quality,
            exercise_minutes,
            exercise_intensity,
            fatigue_level,
            stress_level,
            symptoms,
            astronaut_id
        ))


def delete_measurements(measurement_ids):

    ids = [
        int(measurement_id)
        for measurement_id in measurement_ids
    ]

    if not ids:
        return 0

    placeholders = ", ".join("?" for _ in ids)

    with connect() as con:

        cursor = con.execute(
            f"""
            DELETE FROM measurements
            WHERE id IN ({placeholders})
            """,
            ids
        )

        return cursor.rowcount


def get_measurements(astronaut_id="AST-001"):

    with connect() as con:

        return pd.read_sql_query(
            """
            SELECT *
            FROM measurements
            WHERE astronaut_id = ?
            ORDER BY id
            """,
            con,
            params=(astronaut_id,)
        )



def save_baseline(
    heart_rate,
    temperature,
    oxygen,
    respiratory_rate=None,
    systolic_bp=None,
    diastolic_bp=None,
    radiation_rate=None,
    radiation_dose=None,
    astronaut_id="AST-001"
):

    with connect() as con:

        con.execute("""
            INSERT INTO baseline (
                astronaut_id,
                heart_rate,
                temperature,
                oxygen,
                respiratory_rate,
                systolic_bp,
                diastolic_bp,
                radiation_rate,
                radiation_dose
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)

            ON CONFLICT(astronaut_id) DO UPDATE SET
                heart_rate = excluded.heart_rate,
                temperature = excluded.temperature,
                oxygen = excluded.oxygen,
                respiratory_rate = excluded.respiratory_rate,
                systolic_bp = excluded.systolic_bp,
                diastolic_bp = excluded.diastolic_bp,
                radiation_rate = excluded.radiation_rate,
                radiation_dose = excluded.radiation_dose
        """, (
            astronaut_id,
            heart_rate,
            temperature,
            oxygen,
            respiratory_rate,
            systolic_bp,
            diastolic_bp,
            radiation_rate,
            radiation_dose
        ))


def get_baseline(astronaut_id="AST-001"):

    if not astronaut_id:
        return None

    with connect() as con:

        row = con.execute("""
            SELECT
                heart_rate,
                temperature,
                oxygen,
                respiratory_rate,
                systolic_bp,
                diastolic_bp,
                radiation_rate,
                radiation_dose
            FROM baseline
            WHERE astronaut_id = ?
        """, (astronaut_id,)).fetchone()

    if row is None:
        return None

    return {
        "heart_rate": row[0],
        "temperature": row[1],
        "oxygen": row[2],
        "respiratory_rate": row[3],
        "systolic_bp": row[4],
        "diastolic_bp": row[5],
        "radiation_rate": row[6],
        "radiation_dose": row[7]
    }

def save_baseline(
    heart_rate,
    temperature,
    oxygen,
    respiratory_rate=None,
    systolic_bp=None,
    diastolic_bp=None,
    radiation_rate=None,
    radiation_dose=None,
    astronaut_id="AST-001"
):

    with connect() as con:

        con.execute("""
            INSERT INTO baseline (
                astronaut_id,
                heart_rate,
                temperature,
                oxygen,
                respiratory_rate,
                systolic_bp,
                diastolic_bp,
                radiation_rate,
                radiation_dose
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)

            ON CONFLICT(astronaut_id) DO UPDATE SET
                heart_rate = excluded.heart_rate,
                temperature = excluded.temperature,
                oxygen = excluded.oxygen,
                respiratory_rate = excluded.respiratory_rate,
                systolic_bp = excluded.systolic_bp,
                diastolic_bp = excluded.diastolic_bp,
                radiation_rate = excluded.radiation_rate,
                radiation_dose = excluded.radiation_dose
        """, (
            astronaut_id,
            heart_rate,
            temperature,
            oxygen,
            respiratory_rate,
            systolic_bp,
            diastolic_bp,
            radiation_rate,
            radiation_dose
        ))


def get_baseline(astronaut_id="AST-001"):

    if not astronaut_id:
        return None

    with connect() as con:

        row = con.execute("""
            SELECT
                heart_rate,
                temperature,
                oxygen,
                respiratory_rate,
                systolic_bp,
                diastolic_bp,
                radiation_rate,
                radiation_dose
            FROM baseline
            WHERE astronaut_id = ?
        """, (astronaut_id,)).fetchone()

    if row is None:
        return None

    return {
        "heart_rate": row[0],
        "temperature": row[1],
        "oxygen": row[2],
        "respiratory_rate": row[3],
        "systolic_bp": row[4],
        "diastolic_bp": row[5],
        "radiation_rate": row[6],
        "radiation_dose": row[7]
    }

# Create a new AI conversation
def create_chat_conversation(astronaut_id="AST-001", title="New Chat"):

    with connect() as con:
        cursor = con.execute("""
            INSERT INTO chat_conversations (title, astronaut_id)
            VALUES (?, ?)
        """, (title, astronaut_id))

        return cursor.lastrowid


# Get all conversations of an astronaut
def get_chat_conversations(astronaut_id="AST-001"):

    with connect() as con:
        rows = con.execute("""
            SELECT id, title, created_at
            FROM chat_conversations
            WHERE astronaut_id = ?
            ORDER BY id DESC
        """, (astronaut_id,)).fetchall()

    return [
        {
            "id": row[0],
            "title": row[1],
            "created_at": row[2]
        }
        for row in rows
    ]


# Add AI chat message
def add_chat_message(
    role,
    content,
    astronaut_id="AST-001",
    conversation_id=None
):

    with connect() as con:

        # Use the latest conversation if no ID is provided
        if conversation_id is None:
            row = con.execute("""
                SELECT id
                FROM chat_conversations
                WHERE astronaut_id = ?
                ORDER BY id DESC
                LIMIT 1
            """, (astronaut_id,)).fetchone()

            if row:
                conversation_id = row[0]
            else:
                cursor = con.execute("""
                    INSERT INTO chat_conversations (astronaut_id)
                    VALUES (?)
                """, (astronaut_id,))

                conversation_id = cursor.lastrowid

        con.execute("""
            INSERT INTO chat_messages (
                role, content, astronaut_id, conversation_id
            )
            VALUES (?, ?, ?, ?)
        """, (role, content, astronaut_id, conversation_id))

        # Set conversation title from the first user message
        if role == "user":
            con.execute("""
                UPDATE chat_conversations
                SET title = ?
                WHERE id = ?
                AND title = 'New Chat'
            """, (content[:40], conversation_id))


# Get chat history
def get_chat_history(
    limit=30,
    astronaut_id="AST-001",
    conversation_id=None
):

    with connect() as con:

        if conversation_id is None:
            row = con.execute("""
                SELECT id
                FROM chat_conversations
                WHERE astronaut_id = ?
                ORDER BY id DESC
                LIMIT 1
            """, (astronaut_id,)).fetchone()

            if not row:
                return []

            conversation_id = row[0]

        rows = con.execute("""
            SELECT role, content
            FROM chat_messages
            WHERE astronaut_id = ?
            AND conversation_id = ?
            ORDER BY id DESC
            LIMIT ?
        """, (astronaut_id, conversation_id, limit)).fetchall()

    return [
        {"role": row[0], "content": row[1]}
        for row in reversed(rows)
    ]


# Delete one conversation
def delete_chat_conversation(conversation_id, astronaut_id="AST-001"):

    with connect() as con:

        con.execute("""
            DELETE FROM chat_messages
            WHERE conversation_id = ?
            AND astronaut_id = ?
        """, (conversation_id, astronaut_id))

        con.execute("""
            DELETE FROM chat_conversations
            WHERE id = ?
            AND astronaut_id = ?
        """, (conversation_id, astronaut_id))


# Clear all chat history of an astronaut
def clear_chat_history(astronaut_id="AST-001"):

    with connect() as con:

        con.execute("""
            DELETE FROM chat_messages
            WHERE astronaut_id = ?
        """, (astronaut_id,))

        con.execute("""
            DELETE FROM chat_conversations
            WHERE astronaut_id = ?
        """, (astronaut_id,))

# Add a new astronaut
def add_astronaut(astronaut_id, name):

    with connect() as con:
        con.execute("""
            INSERT INTO astronauts (astronaut_id, name)
            VALUES (?, ?)
        """, (astronaut_id, name))


# Get all astronauts
def get_astronauts():

    with connect() as con:
        rows = con.execute("""
            SELECT astronaut_id, name
            FROM astronauts
            ORDER BY astronaut_id
        """).fetchall()

    return [
        {
            "astronaut_id": row[0],
            "name": row[1]
        }
        for row in rows
    ]
def astronaut_exists(astronaut_id):

    with connect() as con:

        row = con.execute("""
            SELECT 1
            FROM astronauts
            WHERE astronaut_id = ?
        """, (astronaut_id,)).fetchone()

    return row is not None

def delete_astronaut(astronaut_id):
    with connect() as con:

        # Ölçümleri sil
        con.execute(
            "DELETE FROM measurements WHERE astronaut_id = ?",
            (astronaut_id,)
        )

        # Sohbet geçmişini sil
        con.execute(
            "DELETE FROM chat_messages WHERE astronaut_id = ?",
            (astronaut_id,)
        )

        # Baseline tablosunun sütunlarını kontrol et
        columns = [
            row[1]
            for row in con.execute(
                "PRAGMA table_info(baseline)"
            ).fetchall()
        ]

        if "astronaut_id" in columns:
            con.execute(
                "DELETE FROM baseline WHERE astronaut_id = ?",
                (astronaut_id,)
            )
        elif astronaut_id == "AST-001":
            # Eski veritabanı yapısıyla uyumluluk
            con.execute("DELETE FROM baseline WHERE id = 1")

        # Astronotu sil
        cursor = con.execute(
            "DELETE FROM astronauts WHERE astronaut_id = ?",
            (astronaut_id,)
        )

        return cursor.rowcount
