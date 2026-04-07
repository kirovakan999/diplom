import mysql.connector

try:
    conn = mysql.connector.connect(
        host='localhost',
        database='car_audio_shop',
        user='root',
        password='999999'  # замените на свой пароль
    )
    print("✅ Подключение к базе данных успешно!")
    conn.close()
except Exception as e:
    print(f"❌ Ошибка подключения: {e}")