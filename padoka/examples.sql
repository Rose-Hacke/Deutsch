-- Open data/padoka.sqlite with DB Browser for SQLite or sqlite3.
SELECT record_id,document_date,document_number,title
FROM records ORDER BY document_date DESC LIMIT 20;

-- Metadata search; PDF text is indexed separately in files_fts.
SELECT r.* FROM records r JOIN records_fts f ON f.record_id=r.record_id
WHERE records_fts MATCH 'AfD' ORDER BY r.document_date DESC;

-- Search downloaded PDF text and find the corresponding document records.
SELECT DISTINCT r.record_id,r.title,r.citation
FROM files_fts f JOIN record_files rf ON rf.url=f.url
JOIN records r ON r.record_id=rf.record_id
WHERE files_fts MATCH 'Erinnerungskultur';

-- Records whose public catalog does not expose a file link.
SELECT r.record_id,r.title,r.citation FROM records r
WHERE NOT EXISTS(SELECT 1 FROM record_files f WHERE f.record_id=r.record_id);

-- Download failures and the exact original URL.
SELECT url,http_status,error,attempts FROM files WHERE status<>'downloaded';
