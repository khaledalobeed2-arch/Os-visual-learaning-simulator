# Os-visual-learaning-simulator
# OS Concepts Visual Simulator

تطبيق سطح مكتب تفاعلي مبني بـ Python و PyQt6 لشرح مفاهيم أنظمة التشغيل بصريًا، مثل:

- Threads & Concurrency
- Processes & Parallelism
- Race Condition
- Mutex / Monitor
- Semaphore
- Producer / Consumer
- Deadlock
- Starvation

الملف الرئيسي هو [obeed.py](obeed.py).

## المتطلبات

- Python 3.11 أو أحدث
- PyQt6

## التشغيل

```powershell
python obeed.py
```

## وصف سريع

يعرض التطبيق كل مفهوم داخل شاشة مستقلة مع:

- لوحة تحكم لتغيير القيم الأساسية
- مؤشرات حالة ملوّنة
- سجل أحداث حي
- رسومات توضيحية متحركة

## ملاحظات

- الواجهة تعتمد على PyQt6 بالكامل.
- الملف يحتوي على عدة نماذج محاكاة داخل نافذة رئيسية واحدة.
- مناسب للاستخدام التعليمي والعرض التوضيحي داخل الصف أو المختبر.
