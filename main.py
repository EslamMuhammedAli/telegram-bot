import json
import telebot
import os

# ========= الإعدادات الأساسية =========
TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)
DATA_FILE = "user_data.json"

# روابط الخطط التدريبية
PROGRAM_LINKS = {
    "A": "https://drive.google.com/file/d/1DEytOkY7m7LJOyvY3oJHDzFBUQWerq_c/view?usp=drivesdk",
    "B": "https://drive.google.com/file/d/1ZUqJq3Vns7JhH7zb6mB-J_rIrmHSHv0r/view?usp=drivesdk",
    "C": "https://drive.google.com/file/d/109YD2lZTFcLYYJ4NI-eGBCvXD4qACcRt/view?usp=drivesdk",
    "D": "https://drive.google.com/file/d/1a74tj30WRS27ZuaCm88J9UI_uifhzEJc/view?usp=drivesdk",
    "E": "https://drive.google.com/file/d/15QhYbazaAs6RZMeL0pLre4Xf2ATY-8B4/view?usp=drivesdk"
}

DIET_PLAN_LINK = "https://wa.me/201015000540"

# ========= أدوات حفظ الحالة =========
def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

user_data = load_data()

# ========= منطق اختيار البرنامج =========
def select_plan(gender, fat):
    if gender == 'male':
        if fat <= 14:
            return 'A'
        elif fat <= 20:
            return 'B'
        elif fat <= 50:
            return 'C'
    elif gender == 'female':
        if fat <= 20:
            return 'D'
        elif fat <= 50:
            return 'E'
    return None

# ========= المعالجة الرئيسية =========
@bot.message_handler(commands=['start'])
def handle_start(message):
    cid = str(message.chat.id)
    user_data[cid] = {"step": "name"}
    save_data(user_data)
    bot.send_message(message.chat.id, "أهلاً وسهلاً بيك في *Infinity Gym* 🏋️‍♂️\nجاهز نبدأ الرحلة؟ 💪\n\nإيه اسمك؟", parse_mode='Markdown')

@bot.message_handler(func=lambda msg: True)
def handle_message(message):
    cid = str(message.chat.id)
    text = message.text.strip()

    if cid not in user_data:
        user_data[cid] = {"step": "name"}
        bot.send_message(message.chat.id, "يلا نبدأ من الأول 😃\nإيه اسمك؟")
        save_data(user_data)
        return

    state = user_data[cid]

    if state["step"] == "name":
        state["name"] = text.title()
        state["step"] = "age"
        bot.send_message(message.chat.id, f"تشرفنا بيك يا {state['name']} 😃\nكم عمرك يا بطل؟")

    elif state["step"] == "age":
        state["age"] = text
        state["step"] = "gender"
        bot.send_message(message.chat.id, "وإنت ولد ولا بنت؟ 👦👧")

    elif state["step"] == "gender":
        if 'ذكر' in text or 'ولد' in text or 'male' in text.lower():
            state["gender"] = 'male'
        elif 'أنثى' in text or 'بنت' in text or 'female' in text.lower():
            state["gender"] = 'female'
        else:
            bot.send_message(message.chat.id, "من فضلك اختار 'ذكر' أو 'أنثى' 🙏")
            return
        state["step"] = "fat"
        bot.send_message(message.chat.id, "تمام يا كابتن 💪\nاكتبلي نسبة الدهون عندك؟ (مثلاً: 23)")

    elif state["step"] == "fat":
        try:
            fat = float(text)
            state["fat"] = fat
            plan = select_plan(state["gender"], fat)
            if plan:
                state["recommended_plan"] = plan
                bot.send_message(message.chat.id, f"نسبة الدهون دي ممتازة كبداية 🔥\nالبرنامج المناسب ليك هو: *خطة {plan}*", parse_mode='Markdown')
                bot.send_message(message.chat.id, f"📥 حمل خطة التمرين بتاعتك من هنا:\n{PROGRAM_LINKS[plan]}")
                bot.send_message(message.chat.id, "💡 هل ترغب في نظام غذائي يساعدك تحرق دهون بشكل أسرع؟ (اكتب نعم أو لا)")
                state["step"] = "diet"
            else:
                bot.send_message(message.chat.id, "عذرًا، مش قادر أحدد برنامج مناسب. راجع البيانات.")
        except ValueError:
            bot.send_message(message.chat.id, "من فضلك أدخل رقم صحيح لنسبة الدهون (مثلاً: 22.5)")

    elif state["step"] == "diet":
        if 'نعم' in text or 'yes' in text.lower():
            bot.send_message(message.chat.id, "رائع! 💯\nنظام التغذية هو سر النجاح الحقيقي.\nاشترك معانا في برنامج التغذية تحت إشراف كابتن أحمد طه 🥗💪")
            bot.send_message(message.chat.id, f"📲 اشترك الآن من هنا:\n{DIET_PLAN_LINK}")
            bot.send_message(message.chat.id, "هل تحب أرسل لك الجدول التدريبي اليومي بشكل أوتوماتيكي كل صباح؟ ☀️")
        elif 'لا' in text or 'no' in text.lower():
            bot.send_message(message.chat.id, "تمام 💪\nلو غيرت رأيك، أنا موجود 😄")
        else:
            bot.send_message(message.chat.id, "اكتب فقط (نعم) أو (لا) من فضلك 🙏")
        state["step"] = "done"

    else:
        bot.send_message(message.chat.id, "💬 لو تحب تبدأ من جديد اكتب /start\nأو اسألني عن أي حاجة تخص التدريب أو التغذية!")

    save_data(user_data)

import threading
import random
import time
from datetime import datetime, timedelta

# ✅ قائمة الرسائل اليومية (يمكنك استبدالها بقائمتك المكونة من 100 رسالة)
DAILY_MESSAGES = [
    "💪 تمرينك هو بداية رحلتك نحو الجسم اللي بتحلم بيه!",
    "🔥 كل مرة تتمرن فيها، أنت أقرب لهدفك!",
    "💧 اشرب مياه كتير، هتفرق جدًا في الأداء والتركيز.",
    "📲لو عاوز تتابع كابتن اسلام من هنا : https://www.instagram.com/ironaestheticsxx/reels/",
    "📲 اشترك في خطة التغذية المدفوعة مع افضل مدربين السويس تحت اشراف كابتن أحمد طه: https://wa.me/201015000540",
    "🍳 وجبة الإفطار = وقود يومك. اختارها صح.",
    "🧘‍♂️ خصص وقت للراحة والنوم، العضلات بتكبر وأنت نايم.",
    "🧠 العقل السليم في الجسم السليم… خلي هدفك واضح.",
    "🎯 حتى يوم سيء أفضل من يوم ما تمرنتش فيه.",
    "🍳 وجبة الإفطار = وقود يومك. اختارها صح.",
    "🏃‍♂️ 10 دقائق كارديو كل يوم = قلب أقوى وجسم أنشط.",
    "🍗 بروتين كافي = عضلات أقوى. خلي دايمًا معاك مصدر بروتين.",
     "📲لو عاوز تتابع كابتن اسلام من هنا : https://www.instagram.com/ironaestheticsxx/reels/",
    "📅 التزامك بالروتين هو الفرق بين الحلم والواقع.",
    "🍌 موز + زبادي = سناك مثالي قبل التمرين.",
    "🥩 البروتين مش بس للعضلات، كمان للمناعة والشبع.",
    "🚶‍♂️ امشي بعد الأكل 10 دقايق... هتساعد في الهضم.",
    "📏 خليك صبور... الجسم بيتغير لكن مش بين يوم وليلة.",
    "🤝 كل يوم بتلتزم فيه، جسمك بيشكرك.",
    "💡 الجيم مش للعنف، للجمال والقوة والثقة.",
    "📸 صور تقدمك كل أسبوع... هتتشجع جدًا!",
    "🔥 كل نقطة عرق = خطوة أقرب للجسم اللي بتحلم بيه.",
    "🌞 التمرين الصباحي = بداية يوم إيجابي.",
    "📉 عايز تحرق دهون؟ قلل السكر الأبيض.",
    "🍞 العيش الأسمر أفضل من العيش الأبيض… جربه!",
    "💤 نم كويس. النوم الجيد = تعافي أفضل.",
    "🤸‍♀️ المرونة مهمة زي القوة. جرب تمارين إطالة بعد التمرين.",
     "📲لو عاوز تتابع كابتن اسلام من هنا : https://www.instagram.com/ironaestheticsxx/reels/",
    "💪 قوتك مش بس في جسمك... في إرادتك كمان!",
    "🥬 الألياف = هضم صحي وشبع أطول.",
    "🛑 وقف مقارنة نفسك بغيرك... ركز على رحلتك!",
    "📚 العلم قوة! اسألنا عن أي حاجة في التغذية أو التدريب.",
    "🎵 التمرين على أغانيك المفضلة بيرفع الحماس.",
    "📲 تابع صفحة الجيم على فيسبوك: https://www.facebook.com/InfinityGym23/",
    "📲 تابع صفحة الجيم على انستا: https://www.instagram.com/infinity_gym23/?hl=en",
    "🌱 كل أكلك ألوان... كل لون في الخضار له فائدة.",
    "💼 حتى مع شغل كتير، خصص وقت لنفسك وجسمك.",
    "🍎 تفاحة بين الوجبات؟ أحسن من شوكولاتة!",
    "🧂 قلل الملح… بيحبس مياه في الجسم.",
    "🥤 مش كل مشروب صحي… ابعد عن العصائر الصناعية.",
    "💵 استثمر في صحتك قبل ما تضطر تدفع لعلاجك.",
    "🚴‍♂️ جرب تغيير في التمرين… التنوع بيفيد العضلة.",
    "😴 لو تعبان… ريّح! يوم راحة مش خيانة لهدفك.",
    "💭 كل تمرين بتفكر تبطله... تذكر ليه بدأت.",
    "📝 خطط وجباتك قبل ما تجوع.",
    "📦 الوجبات الجاهزة مش لازم تبقى سيئة… اختار الصح.",
     "📲لو عاوز تتابع كابتن اسلام من هنا : https://www.instagram.com/ironaestheticsxx/reels/",
    "🧘‍♀️ صحتك النفسية جزء من رحلتك.",
    "🍽️ كل ببطء… هتحس بالشبع أسرع.",
    "📊 تابع تقدمك بالأرقام والصور.",
    "🧃 العصائر الطبيعية أفضل من الجاهزة، بس خليها بدون سكر.",
    "🚿 دش بارد بعد التمرين = انتعاش عضلي.",
    "📦 وجبة فيها كارب + بروتين بعد التمرين = تعافي أسرع.",
    "💬 اسأل مدربك قبل ما تبدأ نظام قاسي.",
    "🥛 اللبن قليل الدسم أفضل من كامل الدسم في الدايت.",
    "🥜 اللوز وجبة خفيفة رائعة... بس بكميات معتدلة.",
    "⚖️ الميزان مش كل حاجة... راقب شكلك وقوتك كمان.",
    "📲 اشترك في خطة التغذية من هنا: https://wa.me/201015000540",
    "🧠 خليك إيجابي... التغيير بيبدأ من دماغك!",
    "🚴‍♀️ حتى 20 دقيقة مشي يوميًا بتفرق.",
    "📣 قول لصاحبك يتمرن معاك... التحفيز بيزيد.",
    "🥶 ابعد عن المشروبات الغازية… حتى الدايت منها.",
    "💡 كل جسم مختلف... مفيش نظام واحد يناسب الكل.",
    "🏋️ تمرن لنفسك مش لأي حد تاني!",
    "🌟 كل يوم جديد هو فرصة لبداية جديدة.",
    "🍯 معلقة عسل الصبح بتديك طاقة فورية.",
    "📆 حافظ على جدول نومك… ده أساس الصحة.",
    "🍫 الشوكولاتة الداكنة أفضل من العادية... باعتدال.",
    "🫀 القلب محتاج حركة… خليه شغال كل يوم.",
    "🛒 اشتري أكلك وانت شبعان… هتختار الصح.",
    "💪 كل تحدي بتعديه = نسخة أقوى منك.",
    "🎧 حط سماعاتك… وابدأ الجيم بتركيزك الكامل.",
    "📦 سناك صحي في الشنطة هينقذك لما تجوع فجأة.",
    "🚿 ريّح عضلاتك... مش لازم كل يوم تمرين تقيل.",
    "🔥 خلي التزامك أعلى من أعذارك.",
     "📲لو عاوز تتابع كابتن اسلام من هنا : https://www.instagram.com/ironaestheticsxx/reels/",
    "📏 الجسم الرياضي مش بيجي بالساهل… التزم واصبر.",
    "🥕 الجزر وجبة خفيفة ممتازة للدايت.",
    "🎯 التمرين بدون هدف = وقت ضايع.",
    "🥚 بيضة مسلوقة في فطارك = بروتين مجاني!",
    "🍗 صدور الدجاج مصدر بروتين نظيف واقتصادي.",
    "🍌 موزة قبل التمرين = طاقة سريعة.",
    "🥦 البروكلي = كنز فيتامينات… حطه في طبقك!",
    "🍠 البطاطا أفضل من البطاطس المقلية مليون مرة.",
    "🌶️ الفلفل الأحمر = فيتامين C طبيعي.",
    "🧅 البصل والثوم = مضادات حيوية طبيعية.",
    "🥒 الخيار = ترطيب طبيعي.",
    "🧃 عصير ليمون على الريق = تنشيط للجسم.",
    "📵 سيب موبايلك وانت بتتمرن… ركز!",
    "📸 كل شهر صور نفسك… علشان تشوف الفرق الحقيقي.",
     "📲لو عاوز تتابع كابتن اسلام من هنا : https://www.instagram.com/ironaestheticsxx/reels/",
    "🏆 خليك فخور بكل خطوة بتاخدها.",
    "🧘‍♂️ التأمل 5 دقايق يوميًا… ينظف دماغك.",
    "🗓️ التكرار اليومي بيصنع عادة… خليك مستمر.",
    "🥳 جسمك بيتغير... بس مخك كمان بيتطور.",
    "📲 لو محتاج دعم، إحنا دايمًا معاك على https://wa.me/201090070836 💙"
    # ... أكمل باقي الـ 100 رسالة هنا ...
]

# 🧠 تخزين اليوم اللي تم فيه إرسال الرسالة لتجنّب التكرار
last_sent_date = None

def send_daily_messages():
    global last_sent_date
    while True:
        now = datetime.utcnow() + timedelta(hours=3)  # توقيت مصر
        current_date = now.date()

        # الساعة 9 صباحًا ولم يتم الإرسال اليوم
        if now.hour == 9 and last_sent_date != current_date:
            message = random.choice(DAILY_MESSAGES)
            for cid in user_data:
                try:
                    bot.send_message(int(cid), f"🗓️ *رسالة اليوم من Infinity Gym:*\n\n{message}", parse_mode="Markdown")
                except Exception as e:
                    print(f"❌ Failed to send message to {cid}: {e}")

            last_sent_date = current_date
            print(f"✅ Daily message sent on {current_date}")

        time.sleep(60)  # راقب كل دقيقة


# ✅ بدء إرسال الرسائل اليومية تلقائيًا في الخلفية
threading.Thread(target=send_daily_messages, daemon=True).start()


# ========= تشغيل البوت =========
print("🔥 Bot is running...")
bot.polling()
