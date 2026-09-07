# ممیزی کامل Bullish در تایم‌فریم ۳۰ ثانیه

تاریخ ممیزی: `2026-09-07`

ورودی خام:
`market-data/raw/RAW FOREXCOM_XAUUSD 1S FROM 2026-08-18 04-44-40 TO 2026-09-05 00-29-39.json`

مسیر اجرای واقعی:
`indicator/indicator-settings/backend/reaction_bridge.py`

پارامترها:

- جهت: `bullish`
- timeframe: `30`
- timezone: `Asia/Tehran`
- بازهٔ کندل کاملِ قابل محاسبه: `2026-08-18 04:45:00` تا `2026-09-05 00:29:30`
- هیچ CSV، timestamp، قیمت یا خروجی override وارد runtime نشده است.

## نتیجهٔ قطعی

در اجرای کامل runtime، هیچ خطای قطعی محاسباتی در collectionهای عمومی پیدا نشد:

- `calculationValid=false`: صفر
- duplicate identity برای A/S/E/StopAll: صفر
- خروجی خارج از بازه: صفر
- ترتیب زمانی collectionها: صحیح
- collision هم‌زمان source بین A/S/E/StopAll: صفر
- شکاف شماره‌گذاری E: صفر
- violation زمانی پس از اعمال قرارداد واقعی S/E: صفر
- hardcode مربوط به تاریخ، CSV، timestampهای بازبینی‌شده یا خروجی دستی در source runtime: پیدا نشد

تعداد خروجی‌های اجرای واقعی:

| collection | count |
|---|---:|
| reactions | 3189 |
| resets | 1577 |
| blueLines | 1742 |
| aZones | 321 |
| sZones | 159 |
| eZones | 147 |
| stopAlls | 22 |
| orderAudit | 466 |

## مواردی که audit اولیه اشتباه گزارش کرده بود

Audit اولیه ۴۷ مورد chronology violation گزارش کرده بود. این گزارش معتبر نبود، چون:

1. قرارداد Order فقط `orderFirstTime <= orderBreakTime <= orderConfirmationTime` است.
2. `decisionTime` زمان تصمیم چرخهٔ S/E است و می‌تواند برابر break، برابر confirmation یا در main candle بعدی باشد؛ فقط نباید قبل از `sourceTime` باشد.
3. `parentStopEventTime` باید بعد از `parentSourceTime` باشد؛ parent ابتدا ایجاد و بعد متوقف می‌شود.

پس از اصلاح audit با همین قرارداد، تعداد violation برابر صفر شد.

## سه مورد lineage که نیاز به توجه دارند

### S در 2026-08-26 07:15:30

`aSourceIndex=16802` همان source index مربوط به E1 نهایی است. طبق اولویت مالکیت `StopAll > E > S > A`، A در payload عمومی حذف و E مالک source شده است. این نقص محاسبه نیست؛ یک رفتار مورد انتظار visibility است.

### S در 2026-08-28 15:11:00

`aSourceIndex=23256` نیز با E2 نهایی collision مالکیتی دارد و به همان دلیل A جداگانه در payload عمومی دیده نمی‌شود. این مورد هم خطای محاسباتی نیست.

### E2 blue در 2026-08-28 00:06:30

این E به parent با `parentType=E` و source index `21581` ارجاع می‌دهد، اما parent در collection نهایی `eZones` وجود ندارد. در payload عمومی فقط E2 در index `21636` حاضر است. این مورد از روی خروجی عمومی به‌تنهایی قابل حکم قطعی نیست: parent می‌تواند E داخلیِ superseded باشد، یا closure lineage برای parentهای E ناقص باشد.

قابل رفع است، اما فقط با trace داخلیِ E قبل از visibility filtering باید تعیین شود که parent واقعاً accepted بوده یا صرفاً candidate انتقالی. اگر accepted بوده، closure باید برای parentهای E نیز مانند parentهای S بازگردانی شود؛ اگر superseded بوده، باید در گزارش به‌عنوان expected internal lineage ثبت شود و خروجی عمومی تغییری نکند.

## سیزده Order بدون رکورد مستقل در orderAudit

برای ۱۳ S، هندسهٔ Order در خود S کامل است اما همان `(orderFirstIndex, orderBreakIndex)` رکورد جداگانه‌ای در `orderAudit` ندارد. این با قرارداد فعلی سازگار است:

- `orderAudit` یک ledger مستقل است.
- frontend ابتدا Orderهای متصل به S/E/StopAll را رسم می‌کند.
- با `representedOrderKeys` از رسم دوبارهٔ همان Order جلوگیری می‌شود.

بنابراین این ۱۳ مورد فقدان محاسبه نیستند و نباید با افزودن رکورد تکراری اصلاح شوند.

## قابلیت اصلاح و اقدام پیشنهادی

- خطای قطعی محاسباتی: در این اجرای کامل پیدا نشد؛ اصلاح الگوریتمی بدون شاهد جدید نباید انجام شود.
- دو missing A parent: قابل اصلاح نیستند چون حذف عمومی نتیجهٔ مالکیت صحیح E است؛ فقط مستندسازی لازم است.
- parent E با index `21581`: نیازمند یک تست trace داخلی و تصمیم دربارهٔ accepted/superseded بودن parent است. تغییر عمومی قبل از این تست می‌تواند خروجی معتبر را خراب کند.
- ۱۳ Order audit: نیاز به اصلاح ندارد؛ geometry در S موجود و frontend deduplicate می‌کند.

خروجی خام اجرای کامل در `tmp/full-bullish-20260818-0905.json` و گزارش ماشینی در `tmp/full-bullish-audit.json` نگهداری شده‌اند. اسکریپت audit در `tmp/audit_full_bullish.py` قرارداد زمانی بالا را اعمال می‌کند.

