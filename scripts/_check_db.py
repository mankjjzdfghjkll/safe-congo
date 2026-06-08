import sqlite3
conn = sqlite3.connect('database/users.db')
cols = [r[1] for r in conn.execute('PRAGMA table_info(alerts)').fetchall()]
print('COLUMNS:', cols)
rows = conn.execute('SELECT * FROM alerts ORDER BY id DESC LIMIT 15').fetchall()
for r in rows:
    print(r)
conn.close()
