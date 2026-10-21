
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS records(
 record_id TEXT PRIMARY KEY, source_ids TEXT NOT NULL, title TEXT NOT NULL,
 citation TEXT NOT NULL, document_date TEXT, date_candidates TEXT NOT NULL,
 document_number TEXT, electoral_period INTEGER, source_url TEXT NOT NULL,
 first_seen TEXT NOT NULL, last_seen TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS files(
 url TEXT PRIMARY KEY, status TEXT NOT NULL DEFAULT 'pending', local_path TEXT,
 sha256 TEXT, byte_count INTEGER, downloaded_at TEXT, http_status INTEGER,
 attempts INTEGER NOT NULL DEFAULT 0, error TEXT, text_status TEXT, page_count INTEGER);
CREATE TABLE IF NOT EXISTS record_files(
 record_id TEXT NOT NULL REFERENCES records(record_id),
 url TEXT NOT NULL REFERENCES files(url), label TEXT,
 PRIMARY KEY(record_id,url));
CREATE TABLE IF NOT EXISTS queries(
 query_key TEXT PRIMARY KEY, date_from TEXT NOT NULL, date_to TEXT NOT NULL,
 periods TEXT NOT NULL, sref TEXT NOT NULL, source_hits INTEGER,
 fetched_hits INTEGER, expected_records INTEGER, parsed_records INTEGER DEFAULT 0,
 next_start INTEGER DEFAULT 0, completed INTEGER DEFAULT 0,
 observed_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS query_records(
 query_key TEXT NOT NULL REFERENCES queries(query_key),
 record_id TEXT NOT NULL REFERENCES records(record_id),
 PRIMARY KEY(query_key,record_id));
CREATE TABLE IF NOT EXISTS evidence(
 path TEXT PRIMARY KEY, sha256 TEXT NOT NULL, fetched_at TEXT NOT NULL,
 query_key TEXT NOT NULL, start_offset INTEGER NOT NULL, record_count INTEGER NOT NULL);
CREATE VIRTUAL TABLE IF NOT EXISTS records_fts USING fts5(record_id UNINDEXED,title,citation);
CREATE VIRTUAL TABLE IF NOT EXISTS files_fts USING fts5(url UNINDEXED,body);
CREATE INDEX IF NOT EXISTS records_date ON records(document_date);
CREATE INDEX IF NOT EXISTS files_status ON files(status);
CREATE INDEX IF NOT EXISTS record_files_url ON record_files(url);
