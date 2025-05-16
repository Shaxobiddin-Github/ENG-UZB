import json
import os
from datetime import datetime

# Faqat users.json ishlatamiz
USERS_FILE = "users.json"

def load_users():
    """users.json dan ma'lumotlarni o'qiydi."""
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if not content:
                    return {}
                return json.loads(content)
        except json.JSONDecodeError:
            print(f"users.json da JSON xatoligi, bo'sh obyekt qaytarilmoqda")
            return {}
        except Exception as e:
            print(f"users.json dan o'qishda xatolik: {e}")
            return {}
    return {}

def save_users(users):
    """users.json ga ma'lumotlarni saqlaydi."""
    try:
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(users, f, indent=4)
    except Exception as e:
        print(f"Ma'lumotlarni saqlashda xatolik: {e}")

def calculate_level(score):
    """Foydalanuvchi darajasini ball asosida hisoblaydi."""
    if score < 50:
        return "Beginner"
    elif score < 200:
        return "Intermediate"
    else:
        return "Advanced"

def update_word_stat(user_id: str):
    """Foydalanuvchi yangi so'z o'rganganda statistikani yangilaydi."""
    users = load_users()
    user_id = str(user_id)
    
    if user_id not in users:
        users[user_id] = {
            "words_learned": 0,
            "tests": 0,
            "score": 0.0,
            "level": "Beginner",
            "last_updated": str(datetime.now()),
            "completed_lessons": []
        }
    
    users[user_id]["words_learned"] = users[user_id].get("words_learned", 0) + 1
    users[user_id]["score"] = users[user_id].get("score", 0.0) + 1.0
    users[user_id]["level"] = calculate_level(users[user_id]["score"])
    users[user_id]["last_updated"] = str(datetime.now())
    
    save_users(users)
    return users[user_id]

def update_test_stat(user_id: str, score_change: float):
    """Foydalanuvchi test yoki o‘yin yakunlaganda statistikani yangilaydi."""
    users = load_users()
    user_id = str(user_id)
    
    if user_id not in users:
        users[user_id] = {
            "words_learned": 0,
            "tests": 0,
            "score": 0.0,
            "level": "Beginner",
            "last_updated": str(datetime.now()),
            "completed_lessons": []
        }
    
    users[user_id]["tests"] = users[user_id].get("tests", 0) + 1
    users[user_id]["score"] = users[user_id].get("score", 0.0) + score_change
    users[user_id]["level"] = calculate_level(users[user_id]["score"])
    users[user_id]["last_updated"] = str(datetime.now())
    
    save_users(users)
    return users[user_id]

def get_user_stats(user_id: str):
    """Foydalanuvchi statistikasini qaytaradi."""
    users = load_users()
    user_id = str(user_id)
    
    if user_id not in users:
        return {
            "tests": 0,
            "score": 0.0,
            "level": calculate_level(0.0),
            "last_updated": str(datetime.now()),
            "completed_lessons": []
        }
    
    user_data = users.get(user_id, {})
    user_data["tests"] = user_data.get("tests", 0)
    user_data["score"] = user_data.get("score", 0.0)
    user_data["level"] = calculate_level(user_data["score"])
    user_data["completed_lessons"] = user_data.get("completed_lessons", [])
    return user_data