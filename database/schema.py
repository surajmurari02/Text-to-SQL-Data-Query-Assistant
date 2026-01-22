from .connection import get_connection

TABLE_RELATIONSHIPS = """
Table Relationships:
- albums.ArtistId -> artists.ArtistId (Many albums belong to one artist)
- tracks.AlbumId -> albums.AlbumId (Many tracks belong to one album)
- tracks.MediaTypeId -> media_types.MediaTypeId (Track format)
- tracks.GenreId -> genres.GenreId (Track genre)
- invoice_items.TrackId -> tracks.TrackId (Purchased tracks)
- invoice_items.InvoiceId -> invoices.InvoiceId (Invoice line items)
- invoices.CustomerId -> customers.CustomerId (Customer purchases)
- customers.SupportRepId -> employees.EmployeeId (Customer support representative)
- employees.ReportsTo -> employees.EmployeeId (Employee hierarchy)
- playlist_track.PlaylistId -> playlists.PlaylistId (Playlist membership)
- playlist_track.TrackId -> tracks.TrackId (Tracks in playlists)
"""


def get_table_names():
    with get_connection() as conn:
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )
        return [row[0] for row in cursor.fetchall()
                if not row[0].startswith('sqlite_')]


def get_table_schema(table_name):
    with get_connection() as conn:
        cursor = conn.execute(f"PRAGMA table_info({table_name})")
        columns = []
        for row in cursor.fetchall():
            columns.append({
                "name": row[1],
                "type": row[2],
                "not_null": bool(row[3]),
                "primary_key": bool(row[5])
            })
        return columns


def get_sample_data(table_name, limit=3):
    with get_connection() as conn:
        cursor = conn.execute(f"SELECT * FROM {table_name} LIMIT {limit}")
        columns = [description[0] for description in cursor.description]
        rows = cursor.fetchall()
        return [dict(zip(columns, row)) for row in rows]


def format_table_schema(table_name):
    columns = get_table_schema(table_name)

    lines = [f"Table: {table_name}"]
    lines.append("Columns:")

    for col in columns:
        pk_marker = " (PRIMARY KEY)" if col["primary_key"] else ""
        null_marker = " NOT NULL" if col["not_null"] else ""
        lines.append(f"  - {col['name']}: {col['type']}{pk_marker}{null_marker}")

    try:
        samples = get_sample_data(table_name, limit=2)
        if samples:
            lines.append("Sample data:")
            for sample in samples:
                sample_str = ", ".join(f"{k}={repr(v)}" for k, v in list(sample.items())[:4])
                if len(sample) > 4:
                    sample_str += ", ..."
                lines.append(f"  {sample_str}")
    except Exception:
        pass

    return "\n".join(lines)


def get_schema_for_llm():
    tables = get_table_names()

    schema_parts = ["# Chinook Database Schema\n"]
    schema_parts.append("This is a digital music store database with the following tables:\n")

    for table in tables:
        schema_parts.append(format_table_schema(table))
        schema_parts.append("")

    schema_parts.append(TABLE_RELATIONSHIPS)

    return "\n".join(schema_parts)
