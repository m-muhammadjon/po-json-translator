Po Json Translator
==================
---

Loyiha haqida
-
Ko'plab dasturlar dunyoning har qanday joyidan foydalanuvchilarga qulay bo'lishi uchun turli tillarga tarjima
qilinishini talab qiladi. Tarjima jarayoni ko'plab bosqichlardan o'tishi mumkin va vaqt talab qiladigan va xatolar
ko'paytirishi mumkin bo'lgan murakkab ishdir. Tarjima ma'lumotlarini saqlashning eng umumiy formatlari birinchisi
Portable Object (PO) formatidir, bu format ommabop gettext kutubxonasi tomonidan ishlatiladi. Boshqa tarjima formatlari
orasida JSON keng tarqalgan web dasturlarda ishlatiladi. Ushbu loyiha aynan po va json fayllarini tarjima qilib berishga
mo'ljallangan.

Maqsadi
-
Ushbu loyiha yordamida siz po va json fayllarini tezda tarjima qilingan holatga o'tkazishingiz mumkin. Tarjima
jarayonida kichik xatoliklar bo'lishi mumkin shuning uchun tarjima qilib bo'lgandan keyin qayta tekshirish tavsiya
etiladi. Bu noldan tarjima qilib chiqishdan ko'ra ancha samaraliroqdir🙂.

Loyihada ishlatilgan tool'lar
--
Ushbu loyiha Python dasturlash tilining Django Web freymvorkida yozilgan. Loyihaga qo'shimcha ravishda google translator
matnlarni tarjima qilish uchun va polib kutubxonasi po fayllar bilan ishlash uchun ishlatilgan. Tarjimalarni asinxron
backgroundda bajarish uchun Celery va RabbitMQ ishlatilgan. Shuningdek siz tarjimaning natijasini jonli ravishda
ko'rishingiz uchun web socket ishlatilgan. Loyihaga redis cache ham ishlatilingan json fayllaridagi tarjimalarni
qancha foizda ekanligini foydalanuvchiga ko'rsatish uchun.
Loyihada ishlatilgan tool'lar ro'yxati:

- Django 4.1.4
- Celery 5.2.7
- Channels 4.0.0
- Channels-redis 4.0.0
- Polib 1.1.1
- Googletrans 3.1.0a0
- Django-redis 5.2.0
- Redis 4.4.0

To'liq ro'yxat uchun requirements.txt faylini ko'ring.

Loyihani ishga tushirish
-
Loyihani githubdan yuklab olganingizdan keyin loyiha papkasiga kirasiz va .env.example faylidagi hamma ma'lumotlarni
.env fayliga ko'chirasiz.
Linux uchun:

```bash
cp .env.example .env
```

Python virtual muhitini yaratamiz:

```bash
python3 -m venv venv
source venv/bin/activate
```

Kerakli kutubxonalarni o'rnatamiz:

```bash
pip install -r requirements.txt
```

Ma'lumotlar bazasini yaratamiz:

```bash
sudo -u postgres psql
CREATE DATABASE po_json;
```

Migratsiyalarni bajarib olamiz:

```bash
python manage.py migrate
```

Admin panel uchun superuser yaratamiz:

```bash
python manage.py createsuperuser
```

Loyihani ishga tushiramiz:

```bash
python manage.py runserver
```

Shu bilan birgalikda Celery serverni ham ishga tushirishimiz kerak:

```bash
celery -A config worker -l info
```

Loyihaga qanday yordam berish mumkin?
-
Ushbu loyihani kamchiliklari bor tarjima vaqtida qandaydir xatolik yuzaga kelsa 5 daqiqa kutishdan keyin yana qayta
tarjima qilishga urinadi, lekin qayta tarjima qilayotganda yana boshidan boshlaydi tarjimani avvalgi natjia saqlanmay
qoladi. Fayllardagi tilni o'zi aniqlab, berilgan tilga tarjima qilinadigan funksiyani qo'shsa bo'ladi. Va yana
ko'plab funksiyalar qo'shsa bo'ladi.
