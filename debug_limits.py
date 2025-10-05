import sqlite3
from config import Config

# Check database limits
conn = sqlite3.connect('bot_data.db')
cursor = conn.cursor()
cursor.execute("SELECT key, value FROM settings WHERE key LIKE 'limit_%'")
db_limits = cursor.fetchall()
print("Database limits:")
for key, value in db_limits:
    print(f"  {key}: {value}")

# Check config values
print(f"\nConfig values:")
print(f"  MAX_FILE_SIZE_BYTES: {Config.MAX_FILE_SIZE_BYTES}")
print(f"  MAX_FILE_SIZE_MB: {Config.MAX_FILE_SIZE_MB}")

# Test AdminPanel limits loading
from utils.admin_panel import AdminPanel
admin = AdminPanel()
print(f"\nAdminPanel limits:")
print(f"  max_file_size: {admin.limits['max_file_size']}")
print(f"  max_file_size (MB): {admin.limits['max_file_size'] / (1024*1024)}")

# Test file size check
test_file_size = 90 * 1024 * 1024  # 90MB
result = admin.check_user_limits(12345, test_file_size)
print(f"\nTest 90MB file check:")
print(f"  allowed: {result['allowed']}")
print(f"  reason: {result['reason']}")

conn.close()