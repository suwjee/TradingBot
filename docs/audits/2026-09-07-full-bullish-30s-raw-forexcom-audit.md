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
| aZones | 281 |
| sZones | 145 |
| eZones | 147 |
| stopAlls | 22 |
| orderAudit | 464 |

## مواردی که audit اولیه اشتباه گزارش کرده بود

Audit اولیه ۴۷ مورد chronology violation گزارش کرده بود. این گزارش معتبر نبود، چون:

1. قرارداد Order فقط `orderFirstTime <= orderBreakTime <= orderConfirmationTime` است.
2. `decisionTime` زمان تصمیم چرخهٔ S/E است و می‌تواند برابر break، برابر confirmation یا در main candle بعدی باشد؛ فقط نباید قبل از `sourceTime` باشد.
3. `parentStopEventTime` باید بعد از `parentSourceTime` باشد؛ parent ابتدا ایجاد و بعد متوقف می‌شود.

پس از اصلاح audit با همین قرارداد، تعداد violation برابر صفر شد.

## اصلاح مالک dominant و سه A نارنجی

نسخهٔ قبلی انتخاب dominant، priority و شمارهٔ E را پیش از chronology stop
مقایسه می‌کرد. در نتیجه `E6 red` قدیمی می‌توانست پس از پایان lifecycle خود نیز
مرز Aهای جدید را کنترل کند. قاعدهٔ عمومی اصلاح شد: جدیدترین main candle حاوی
strict stop ابتدا انتخاب می‌شود؛ priority و شماره فقط stopهای همان candle را
حل می‌کنند.

پس از این اصلاح، candidateهای A در `2026-08-20 08:44:00`، `09:08:00` و
`10:25:30` داخل engine باقی می‌مانند ولی calculation-valid عمومی نیستند و در
`aZones` یا chart ظاهر نمی‌شوند. A صحیح `09:49:00` حفظ شده است. هیچ timestamp
یا مقدار داده در runtime استفاده نشده است.

این اصلاح دو missing A parent قبلی را نیز حذف کرد؛ Sهای وابسته به آن Aهای
نامعتبر دیگر وارد payload عمومی نمی‌شوند.

## lineage باقی‌مانده

### E2 blue در 2026-08-28 00:06:30

این E به parent با `parentType=E` و source index `21581` ارجاع می‌دهد، اما parent در collection نهایی `eZones` وجود ندارد. در payload عمومی فقط E2 در index `21636` حاضر است. این مورد از روی خروجی عمومی به‌تنهایی قابل حکم قطعی نیست: parent می‌تواند E داخلیِ superseded باشد، یا closure lineage برای parentهای E ناقص باشد.

قابل رفع است، اما فقط با trace داخلیِ E قبل از visibility filtering باید تعیین شود که parent واقعاً accepted بوده یا صرفاً candidate انتقالی. اگر accepted بوده، closure باید برای parentهای E نیز مانند parentهای S بازگردانی شود؛ اگر superseded بوده، باید در گزارش به‌عنوان expected internal lineage ثبت شود و خروجی عمومی تغییری نکند.

## شش Order بدون رکورد مستقل در orderAudit

برای ۶ S، هندسهٔ Order در خود S کامل است اما همان `(orderFirstIndex, orderBreakIndex)` رکورد جداگانه‌ای در `orderAudit` ندارد. این با قرارداد فعلی سازگار است:

- `orderAudit` یک ledger مستقل است.
- frontend ابتدا Orderهای متصل به S/E/StopAll را رسم می‌کند.
- با `representedOrderKeys` از رسم دوبارهٔ همان Order جلوگیری می‌شود.

بنابراین این ۶ مورد فقدان محاسبه نیستند و نباید با افزودن رکورد تکراری اصلاح شوند.

## قابلیت اصلاح و اقدام پیشنهادی

- خطای قطعی محاسباتی: در این اجرای کامل پیدا نشد؛ اصلاح الگوریتمی بدون شاهد جدید نباید انجام شود.
- سه A نارنجی: با انتخاب chronological مالک dominant اصلاح شدند؛ candidate
  داخلی‌اند و خروجی معتبر عمومی نیستند.
- parent E با index `21581`: نیازمند یک تست trace داخلی و تصمیم دربارهٔ accepted/superseded بودن parent است. تغییر عمومی قبل از این تست می‌تواند خروجی معتبر را خراب کند.
- ۶ Order audit: نیاز به اصلاح ندارد؛ geometry در S موجود و frontend deduplicate می‌کند.

خروجی خام اجرای کامل پس از اصلاح در `tmp/full-bullish-dominant-stop-fix.json` و گزارش ماشینی در `tmp/full-bullish-audit.json` نگهداری شده‌اند. اسکریپت audit در `tmp/audit_full_bullish.py` قرارداد زمانی بالا را اعمال می‌کند.
