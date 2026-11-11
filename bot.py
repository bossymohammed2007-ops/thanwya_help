import urllib.request
import urllib.parse
import json
import time

TOKEN = "9188986332:AAFqy6cROfAr_rT8q0mMSs1i4tYcbEdiaXk"
ADMIN_GROUP_ID = -6477543937
URL = f"https://api.telegram.org/bot{TOKEN}/"

messages_map = {}
user_choice = {}

def call(method, params):
    data = urllib.parse.urlencode(params).encode()
    with urllib.request.urlopen(URL + method, data=data) as r:
        return json.loads(r.read())

def send_message(chat_id, text, reply_markup=None):
    params = {"chat_id": chat_id, "text": text}
    if reply_markup:
        params["reply_markup"] = json.dumps(reply_markup)
    return call("sendMessage", params)

def forward_message(to_chat, from_chat, msg_id):
    return call("forwardMessage", {"chat_id": to_chat, "from_chat_id": from_chat, "message_id": msg_id})

def main_keyboard():
    return {
        "keyboard": [
            [{"text": "الكتب الخارجية 2027"}, {"text": "ليالي الامتحان 2026"}, {"text": "كتب المراجعة النهائية 2026"}],
            [{"text": "النماذج الإرشادية"}, {"text": "كتب المفاهيم"}, {"text": "امتحانات السنوات السابقة"}],
            [{"text": "ملخصات ومذكرات لكل المواد"}, {"text": "النماذج الإرشادية 2025 بالإجابات"}, {"text": "ليالي الامتحان 2025"}],
            [{"text": "كتب المراجعة النهائية 2025 كلها"}, {"text": "ملخصات المواد غير المضافة"}, {"text": "كتب المدرسة"}],
            [{"text": "جريدة الجمهورية كل المواد"}, {"text": "طريقة التعامل مع البابل شيت"}, {"text": "بابل شيت للتدرب"}],
            [{"text": "برامج للـ pdf أو السبورة البيضاء"}]
        ],
        "resize_keyboard": True,
        "one_time_keyboard": False
    }

ALL_BUTTONS = ["الكتب الخارجية 2027", "ليالي الامتحان 2026", "كتب المراجعة النهائية 2026", "النماذج الإرشادية", "كتب المفاهيم", "امتحانات السنوات السابقة", "ملخصات ومذكرات لكل المواد", "النماذج الإرشادية 2025 بالإجابات", "ليالي الامتحان 2025", "كتب المراجعة النهائية 2025 كلها", "ملخصات المواد غير المضافة", "كتب المدرسة", "جريدة الجمهورية كل المواد", "طريقة التعامل مع البابل شيت", "بابل شيت للتدرب", "برامج للـ pdf أو السبورة البيضاء"]

print("Bot is running")
offset = None
while True:
    try:
        params = {"timeout": 10}
        if offset:
            params["offset"] = offset
        data = urllib.parse.urlencode(params).encode()
        with urllib.request.urlopen(URL + "getUpdates", data=data) as r:
            updates = json.loads(r.read()).get("result", [])

        for u in updates:
            offset = u["update_id"] + 1
            msg = u.get("message")
            if not msg:
                continue

            chat = msg["chat"]
            chat_id = chat["id"]
            chat_type = chat["type"]
            text = msg.get("text", "")
            msg_id = msg["message_id"]
            sender = msg.get("from", {})
            first_name = sender.get("first_name", "صديقنا")

            if chat_id == ADMIN_GROUP_ID and "reply_to_message" in msg:
                orig_id = msg["reply_to_message"]["message_id"]
                user_id = messages_map.get(orig_id)
                if user_id:
                    send_message(user_id, text)
                continue

            if chat_type == "private":
                if text == "/start":
                    # دي رسالة الترحيب اللي هتتبعت اول ما يدوس start
                    send_message(chat_id, "ثانويتك مشوار.. وإحنا معاك في كل خطوة ❤️\nأهلاً بيك في بوت الثانوية العامة 🎓", reply_markup=main_keyboard())
                    res = forward_message(ADMIN_GROUP_ID, chat_id, msg_id)
                    try:
                        messages_map[res["result"]["message_id"]] = chat_id
                    except:
                        pass

                elif text in ALL_BUTTONS:
                    user_choice[chat_id] = text
                    send_message(chat_id, f"تمام {first_name}، اخترت: {text}\nابعت رسالتك دلوقتي وهتوصل للإدارة:", reply_markup=main_keyboard())

                elif text:
                    res = forward_message(ADMIN_GROUP_ID, chat_id, msg_id)
                    try:
                        admin_msg_id = res["result"]["message_id"]
                        messages_map[admin_msg_id] = chat_id
                    except:
                        pass
                    send_message(chat_id, "تم استلام رسالتك، هنرد عليك قريب ❤️", reply_markup=main_keyboard())

    except Exception as e:
        print("خطأ:", e)
    time.sleep(1)
