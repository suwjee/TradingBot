# مرجع جامع الگوریتم محاسبات اندیکاتور — روند صعودی

> وضعیت سند: توصیف کدمحورِ رفتار موجود در `D:\My-Projects\TradingBot`
> تاریخ بررسی: 2026-09-05
> منطقهٔ زمانی محاسبات و نمایش زمان: `Asia/Tehran`
> دامنه: فقط خروجی `direction = "bullish"`؛ Reactionهای نزولی فقط تا حدی توضیح داده می‌شوند که نقش Order ورودی برای S و E صعودی دارند.

## 1. هدف، مرجع و حدود اعتبار

این سند برای یک هوش مصنوعی یا توسعه‌دهنده‌ای نوشته شده است که هیچ شناخت قبلی از پروژه ندارد. هدف آن بازسازی جزئی و مرحله‌به‌مرحلهٔ رفتار محاسباتی فعلی اندیکاتور صعودی از روی کد اجرایی `TradingBot` است، نه بازنویسی یک روایت قدیمی یا پیشنهاد یک الگوریتم جدید.

مرجع اصلی و نهایی این سند فایل‌های اجرایی فعلی `D:\My-Projects\TradingBot` هستند. فایل‌های الگوریتمی `D:\My-Projects\Prj-1` فقط برای تطبیق واژگان و یافتن اختلاف‌های احتمالی مرور شدند و هیچ قاعده‌ای صرفاً از آن‌ها وارد این سند نشده است. در snapshot حاضر، فایل‌های Reaction، Blue، A، S، E و bridge میان دو checkout اختلاف دارند؛ فقط StopAll یکسان بود. بنابراین هر جا متن قدیمی با رفتار `TradingBot` ناسازگار باشد، رفتار `TradingBot` مبناست.

این سند «رفتار فعلی کد» را بیان می‌کند، نه این ادعا را که تمام رفتار فعلی از نظر کسب‌وکار تأیید شده است. در زمان بررسی، syntax تمام فایل‌های Python فعال سالم بود و همهٔ 92 آزمون Node پاس شدند؛ با این حال چند آزمون محاسباتی Python شکست داشتند که در بخش 22 ثبت شده‌اند.

## 2. فایل‌های مرجع فعال

مسیرهای زیر نسبت به ریشهٔ `D:\My-Projects\TradingBot` هستند:

- Reaction و Reset:
  `indicator/Modules/1_reaction-detector/app/Reaction-detection-new.py`
- Blue Line:
  `indicator/Modules/2_blue-line/app/blue_line.py`
- A:
  `indicator/Modules/3_A-zone/app/a_detector.py`
- S:
  `indicator/Modules/4_S-zones/app/s_detector.py`
- E و Order ledger:
  `indicator/Modules/5_E-zones/app/e_detector.py`
- StopAll:
  `indicator/Modules/6_StopAll/app/stopall_detector.py`
- orchestration، تبدیل زمان، تجمیع کندل، reconcile و serialization:
  `indicator/indicator-settings/backend/reaction_bridge.py`
- API، اعتبارسنجی inventory، cache و اجرای Python:
  `lightweight-charts/vite.config.js`
- مصرف و رسم payload در مرورگر:
  `lightweight-charts/src/main.js`

نسخه‌های اعلام‌شده در کد فعلی:

- Reaction: `9.3.0`
- Blue Line: bridge مقدار `2.0.1` را در payload می‌گذارد؛ فایل Blue ثابت نسخهٔ مستقل ندارد.
- A: `1.4.0`
- S: `4.1.1`
- E: `6.1.0`
- StopAll: `1.3.0`

SHA-256 فایل‌های محاسباتی در لحظهٔ بررسی:

```text
Reaction  6D7FC7F870BF59F0437536B212FEEC2D0FEF3A8B45CA9E7A535FCB5502FF01D3
Blue      8227E3464C66B5580823342296B1E904DBBCAA5D47CFD3537FA7C5786090FC0F
A         023450E0EDB848990CC031F683EF56761F88CF43C9402902031456B9E6DE8675
S         CE48E941188551D496DCEF6BAF9E43D380CB1F7B62794AD0D299EA53732C146B
E         AFF8E9F61FAD8D3B7E011AFC9B939570EBF21AE7F509A0A1D8B4172C9F35F24D
StopAll   404EF8B5DC17A380C7A9A7F0969944467F6024B2FB78E6BA6BE39C0C391B455D
Bridge    2F4EB33A332E9F59D56825E981107938D1E5640C1653943C8A16AEAB484208EC
Vite      BF943CCDABF1CF0E4CAC108985D122CB78C6A929464932612F36D6CB58E1D190
```

هش‌ها برای اثبات snapshot هستند. اگر یکی از آن‌ها تغییر کند، این سند باید دوباره با کد تطبیق داده شود.

## 3. تصویر کلان و مالکیت محاسبه

ترتیب مفهومی pipeline صعودی چنین است:

```text
RAW 1-second candles
    ↓ validation / time conversion / timeframe aggregation
Bullish Reaction + Bullish Reset
    ↓
Bullish Blue Line
    ↓
Bullish A
    ↓
Bullish S  ← Bearish Reaction + Bearish Reset به‌عنوان Order geometry
    ↓
Bullish E  ← همان Order geometry و Order lifecycle
    ↓
StopAll
    ↺ fixed-point feedback into E sequence resets
    ↓
visibility / ownership filtering / JSON serialization
    ↓
browser rendering (بدون محاسبهٔ مجدد قواعد)
```

مالک حقیقت محاسبات Python است. کد مرورگر فقط objectهای برگشتی را می‌سازد، پنهان/نمایان می‌کند، رنگ یا موقعیت دستی را نگه می‌دارد و آن‌ها را رسم یا export می‌کند. مرورگر نباید Reaction، Blue، A، S، E یا StopAll را دوباره محاسبه کند.

برای خروجی صعودی، اجرای Bearish Reaction یک dependency اجباری است، زیرا Order مخالف روند صعودی، Reaction نزولی است. این موضوع به معنی تولید یا شرح کامل اندیکاتور روند نزولی در این سند نیست.

## 4. اصول مشترک و قراردادهای پایه

### 4.1. دقت عددی

- تمام OHLCها در Python از طریق `Decimal(str(value))` ساخته می‌شوند.
- تصمیم‌های الگوریتمی نباید با `float`، تقریب، tolerance یا گردکردن دلخواه جایگزین شوند.
- قیمت‌ها در JSON نهایی به رشته تبدیل می‌شوند تا دقت Decimal حفظ شود.
- مساوی‌بودن سطح، شکست یا stop نیست؛ تقریباً همهٔ رویدادهای شکست با نابرابری strict تعریف شده‌اند.

برای روند صعودی:

```text
شکست بالایی: High > level
شکست پایینی / stop: Low < level
High == level یا Low == level رویداد محسوب نمی‌شود.
```

### 4.2. رنگ کندل

در bridge:

```text
Open <= Close  => GREEN
Open > Close   => RED
```

پس doji با `Open == Close` در runtime یک کندل `GREEN` است. حالت جداگانهٔ `DOJI` در ورودی runtime ساخته نمی‌شود.

### 4.3. زمان اصلی و زمان دقیق

دو وضوح زمانی هم‌زمان وجود دارد:

- کندل اصلی یا main candle با timeframe انتخاب‌شده؛ مثلاً 30 ثانیه.
- کندل lower/second که در عمل bucket یک‌ثانیه‌ای است.

زمان کندل اصلی معمولاً زمان شروع bucket است. رویدادهایی مانند break، stop، reset یا عبور candidate تا جای ممکن دارای `event_time` دقیق یک‌ثانیه‌ای هستند. اگر دو شرط متضاد داخل یک main candle رخ دهند، ترتیب secondها تعیین‌کننده است؛ ترتیب شاخص main candle به‌تنهایی کافی نیست.

### 4.4. قاعدهٔ tie برای extrema

قاعدهٔ tie در همه‌جا یکسان نیست و باید همان helper مالک رعایت شود:

- در بسیاری از extremaهای Reaction و A، اولین منبع در تساوی حفظ می‌شود.
- در بعضی مسیرهای S، به‌ویژه candidate ساده یا boundary Type 3، آخرین کندل در تساوی انتخاب می‌شود.
- هرگز یک قاعدهٔ عمومی «همیشه اولین» یا «همیشه آخرین» به کل pipeline تحمیل نشود.

### 4.5. chronology و ownership

- هر object علاوه بر قیمت، source index/time و decision index/time دارد.
- object نمی‌تواند از داده‌ای استفاده کند که بعد از decision آن رخ داده است.
- object پایین‌دستی باید provenance والد خود را حفظ کند.
- برخوردهای هم‌زمان با ترتیب دقیق رویدادها حل می‌شوند.
- suppression بصری یا ownership نهایی، رکورد محاسباتی بالادستی را از حافظهٔ محاسبات حذف نمی‌کند مگر helper صریحاً آن را filter کند.

## 5. ورودی، اعتبارسنجی، زمان و aggregation

### 5.1. قرارداد candle inventory در Vite

داده باید یک آرایهٔ غیرخالی باشد. هر ردیف دقیقاً کلیدهای زیر را دارد:

```json
{"time": 0, "open": 0, "high": 0, "low": 0, "close": 0}
```

قواعد:

- `time` باید integer امن، مثبت و برحسب Unix second باشد.
- OHLC باید finite باشد.
- `high` باید بزرگ‌تر یا مساوی open/low/close باشد.
- `low` باید کوچک‌تر یا مساوی open/high/close باشد.
- زمان‌ها باید strictly increasing باشند.
- duplicate یا عقب‌گرد زمانی نامعتبر است.
- کلید اضافه یا کلید گمشده نامعتبر است.

### 5.2. محدودهٔ raw که به Python می‌رسد

فیلتر raw در bridge چنین است:

```text
from <= raw.time < to + timeframe
```

دلیل انتهای بازشده این است که bucket نهایی تا `to` بتواند با secondهای باقی‌ماندهٔ همان timeframe کامل شود. بنابراین دادهٔ بعد از `to` تا پیش از `to + timeframe` ممکن است در OHLC bucket نهایی اثر بگذارد.

### 5.3. تبدیل منطقهٔ زمانی

- epoch ورودی به datetime منطقهٔ `Asia/Tehran` تبدیل می‌شود.
- detectorها با datetime بدون timezone ولی دارای معنای Tehran کار می‌کنند.
- هنگام serialization، همان datetime با timezone تهران دوباره به epoch second تبدیل می‌شود.
- برای گزارش انسانی، datetime کامل و timezone باید ذکر شود؛ timestamp بدون timezone برای تحلیل دستی کافی نیست.

### 5.4. ساخت bucketها

برای هر raw row:

```text
one_second_bucket = floor(time / 1) * 1
main_bucket       = floor(time / timeframe) * timeframe
```

تجمیع هر bucket:

```text
Open  = Open اولین row
High  = بیشینهٔ Highها
Low   = کمینهٔ Lowها
Close = Close آخرین row
```

بعد از aggregation، کندل‌های main قابل‌ارائه آن‌هایی هستند که زمان شروعشان در بازهٔ بستهٔ `[from, to]` باشد.

نکتهٔ مرزی مهم: اگر `from` دقیقاً با مرز timeframe هم‌تراز نباشد، raw filter ممکن است داده‌ای از بخش میانی یک bucket را بگیرد که floor آن پیش از `from` است. آن bucket از presentation range کنار گذاشته می‌شود؛ اما full-context محاسبه روی لیست bucketهای ساخته‌شده از همین raw subset انجام می‌شود. بنابراین این پیاده‌سازی را نباید معادل دریافت تاریخچهٔ نامحدود قبل از `from` دانست.

### 5.5. cache و source fingerprint

Vite cache key را از این اجزا می‌سازد:

- نسخهٔ قرارداد cache: `engine-content-v1`
- SHA-256 محتوای تمام هفت فایل محاسباتی فعال
- شناسهٔ dataset
- mtime فایل داده
- timeframe
- from/to
- direction
- گزینهٔ blueLines

مسیر cache مفهومی:

```text
primary-cache/indicator-calculations/{symbol}/{timeframe}s/{direction}/{from}-{to}--{digest}.json
```

اگر engine در میانهٔ محاسبه تغییر کند، نتیجه ذخیره نمی‌شود. cache قدیمیِ فاقد fingerprint جدید serve نمی‌شود.

## 6. مدل دادهٔ Reaction و Reset

هر Candle محاسباتی شامل این معناهاست:

- `index`: موقعیت در آرایهٔ main candles.
- `timestamp` و `display_time`.
- `tag`: GREEN یا RED.
- `open/high/low/close`: Decimal.

Reaction صعودی دست‌کم این provenance را حمل می‌کند:

- شمارهٔ ترتیبی.
- mode: حالت آغازین A یا حالت عادی B.
- `First`: کندل قرمز مالک شروع setup.
- `BoxTop`: سطح شکست بالایی و کندل منبع آن.
- `BoxBottom`: کف reaction و کندل منبع آن.
- `Break`: main candle تأیید که `High > BoxTop` در آن رخ داده است.
- زمان دقیق break در lower candles.
- anchor یا leg boundary و منبع آن برای مالکیت/ابطال.

Reset صعودی شامل:

- main index/time ریست.
- `second_time` دقیق اولین second که شرط را شکسته است.
- `broken_level`.
- `from_first_idx` که reset را به reaction/leg مالک متصل می‌کند.

## 7. Reaction صعودی — حالت آغازین Mode A

### 7.1. هدف Mode A

Mode A اولین Reaction صعودی معتبر را بدون داشتن Reaction قبلی می‌سازد. detector داخلی ابتدا یک leg-open floor و در صورت امکان یک RED anchor نگه می‌دارد.

### 7.2. تشخیص FirstRed

کاندید FirstRed باید:

1. خودش `RED` باشد.
2. کندل قبلی `GREEN` باشد.
3. شرط کف مرجع را نقض نکرده باشد.

اگر anchor موجود است:

```text
FirstRed.Low >= anchor.Low
```

اگر anchor وجود ندارد، یکی از این دو کافی است:

```text
FirstRed.Low >= previousGreen.Low
یا
FirstRed.Low >= legOpenLow
```

در بعضی مسیرهای invalidation، اگر هم Low کندل GREEN قبلی و هم Low کندل RED فعلی زیر anchor بیفتند، anchor پاک می‌شود و scan ادامه پیدا می‌کند.

### 7.3. ساخت Box اولیه

برای FirstRed:

- run پیوستهٔ GREEN بلافاصله قبل از آن پیدا می‌شود.
- `BoxTop` بیشترین High آن run در مقایسه با High خود FirstRed است.
- اگر `green_high == first_red.high` باشد، منبع قدیمی‌تر GREEN حفظ می‌شود.
- `BoxBottom = FirstRed.Low` و منبع آن FirstRed است.
- anchor/leg floor و منبعش داخل candidate ذخیره می‌شود.

### 7.4. به‌روزرسانی و ابطال candidate

تا پیش از break:

- هر `Low` پایین‌تر از BoxBottom، کف candidate را پایین می‌برد.
- فقط `High > BoxTop` تأیید است.
- `High == BoxTop` هیچ رویدادی نیست.
- invalidation مالک فقط با `Low < anchor/legFloor` رخ می‌دهد.

اگر invalidation و break در یک main candle قابل وقوع باشند، lower candles تصمیم می‌گیرند:

- اگر first lower low زیر boundary زودتر رخ دهد، candidate باطل است.
- اگر first lower high بالای BoxTop زودتر رخ دهد، Reaction تأیید می‌شود.

### 7.5. تأیید و same-candle reset

در main candle تأیید، scan lower از زمان منبع eligible BoxTop تا انتهای candle انجام می‌شود:

1. پایین‌ترین Low پیش از اولین `High > BoxTop` دنبال می‌شود.
2. همان Low می‌تواند BoxBottom نهایی را بهبود دهد.
3. Low پایین‌تری که بعد از breakout رخ داده باشد نباید BoxBottom Reaction تأییدشده را بازنویسی کند.
4. اگر بعد از breakout، lower candle بعدی `Low < confirmed BoxBottom` بسازد، Reset همان main candle ثبت می‌شود و `second_time` آن lower candle است.

این تفکیک برای جلوگیری از نگاه‌به‌آینده داخل یک کندل بزرگ ضروری است.

## 8. Reaction صعودی — حالت عادی Mode B

بعد از اولین Reaction:

- detector یک running high و منبعش نگه می‌دارد.
- دیدن کندل RED می‌تواند candidate جدید Mode B را باز کند.
- `BoxTop` از بیشینهٔ running high و High همان RED ساخته می‌شود.
- `BoxBottom` از پایین‌ترین Low بعد از منبع BoxTop تا FirstRed تعیین می‌شود.
- در تساوی extrema، helper مربوطه provenance تعیین‌شدهٔ خودش را نگه می‌دارد.

candidate عادی:

- با Low پایین‌تر، BoxBottom را به‌روزرسانی می‌کند.
- با `High > frozen BoxTop` تأیید می‌شود.
- BoxTop پس از ساخت candidate یک سطح frozen برای شرط break است؛ نباید با هر high جدید بی‌قاعده جابه‌جا شود.

پس از confirmation، اگر candle تأیید `RED` باشد و post-breakout Reset نداشته باشد، کد می‌تواند remainder همان confirmation candle را برای seed کردن Mode B بعدی بررسی کند. helper فعلی در بعضی محاسبات extrema از کل confirmation main candle استفاده می‌کند و در tie اولین extreme را انتخاب می‌کند؛ بنابراین بازنویسی آن به یک مدل سادهٔ «همیشه از کندل بعد» رفتار را تغییر می‌دهد.

## 9. Reset صعودی و بازیابی مستقیم پس از Reset

### 9.1. شرط Reset

پس از Reaction تأییدشده:

```text
Reset وقتی رخ می‌دهد که Low < lastConfirmed.BoxBottom
```

تساوی با BoxBottom Reset نیست. اولین second عبوری زمان دقیق Reset است.

اگر Reset و break یک candidate جدید در یک main candle باشند، ترتیب secondها مالک نتیجه است.

### 9.2. اثر Reset بر state

Reset:

- state عادی candidate را پاک می‌کند.
- provenance reaction شکسته‌شده را در Reset نگه می‌دارد.
- جست‌وجوی direct same-direction reaction را از بعد از reset آغاز می‌کند.

### 9.3. direct candidate پس از Reset

برای recovery مستقیم:

1. FirstRed بعد از Reset باید بعد از GREEN باشد.
2. run پیوستهٔ GREEN و REDهای مجاور آن بررسی می‌شوند.
3. اگر FirstRed.Low زیر local floor باشد، candidate رد می‌شود.
4. BoxTop از بیشترین High context تا First ساخته می‌شود.
5. leg floor کمترین Low از reset تا پیش از First است و منبعش anchor candidate می‌شود.

در scan candidate:

- `Low < legBoundary` پیش از `High > BoxTop` مالک را باطل می‌کند.
- اگر هر دو در یک main candle باشند، ترتیب secondها تعیین‌کننده است.
- Low پایین‌تر BoxBottom را اصلاح می‌کند.
- High strict بالاتر Reaction را تأیید می‌کند.
- `blocked_through` مانع شروع recovery تو‌در‌تو پیش از پایان محدودهٔ candidate باطل‌شده می‌شود.

## 10. geometryهای Reaction مورد استفادهٔ E

Reaction engine فقط producer فهرست Reaction نیست؛ E از APIهای geometry آن نیز استفاده می‌کند.

### 10.1. Order_A geometry بعد از gate

`first_order_reaction_after_gate` برای Order مستقیم استفاده می‌شود.

- reaction history فقط تا confirmationهایی معتبر است که از gate دقیق جلوتر نرفته باشند.
- اگر یک owner مخالف قبل از gate فعال باشد، race میان outer boundary آن و gate boundary با lower seconds حل می‌شود.
- برای Order نزولی داخل روند صعودی:

```text
High > ownerOuterBoundary  => restart
Low  < gateCandle.Low      => continue
```

- اولین geometry کامل معتبر انتخاب می‌شود.
- در confirmationهای هم‌زمان، candidate با کوچک‌ترین `first_idx` مقدم است.

### 10.2. Order_B geometry از reset-leg

`first_simple_geometry_after_gate` برای Order_B استفاده می‌شود.

- context Reset اصلی حفظ می‌شود.
- First باید در gate candle یا بعد از آن باشد.
- candidate مالک باید outer boundary خود را تا confirmation زنده نگه دارد.
- geometry ساخته‌شده می‌تواند reaction number صفر داشته باشد، چون لزوماً عضو عادی فهرست Reactionهای منتشرشده نیست.

### 10.3. helperهای غیرمسیر فعال

توابعی مانند `_partition_intrabar_turn_boundary`، مسیر مستقل `_structural_gate` و API عمومی `first_geometric_reaction` در call path اصلی bridge فعلی استفاده نمی‌شوند. وجود آن‌ها نباید به‌تنهایی به‌عنوان بخشی از الگوریتم runtime مستند یا دوباره پیاده‌سازی شود.

## 11. Blue Line صعودی

### 11.1. ورودی و نسبت

Blue از Reactionها و Resetهای صعودی استفاده می‌کند:

```text
FIBONACCI_RATIO = Decimal("0.618")
```

برای Reaction آغازین Mode A، reference از `anchor_value` گرفته می‌شود و اگر موجود نباشد `leg_boundary` استفاده می‌شود. برای Reaction عادی، reference برابر BoxBottom Reaction قبلی است.

سطح فیبوناچی:

```text
fib = current.BoxTop - 0.618 * (current.BoxTop - reference)
```

### 11.2. شمارش strike

از First تا Break به‌صورت inclusive scan می‌شود.

- strike جدید وقتی شکل می‌گیرد که `Low < fib` باشد، یا اگر extreme تأییدشده‌ای داریم `Low < lastConfirmedExtreme` باشد.
- equality strike نیست.
- Low پایین‌تر pending strike را جایگزین می‌کند.
- اولین GREEN بعد از pending، آن را تأیید می‌کند.
- چون doji در bridge GREEN است، doji می‌تواند pending را تأیید کند.

اگر در پایان Reaction هنوز pending باقی بماند، lower candles confirmation بررسی می‌شوند. penetration scale باید پیش از یا هم‌زمان با `High > BoxTop` رخ داده باشد. second تعیین‌کننده به main candle منبع map می‌شود.

### 11.3. scale candidate

```text
isScale = previousStrikeCount exists
          and currentStrikeCount > previousStrikeCount
```

پس اولین Reaction بدون count قبلی scale نیست. count حتی در بعضی حالت‌هایی که line به دلیل spacing منتشر نمی‌شود، state مقایسهٔ بعدی را جلو می‌برد.

### 11.4. spacing lock

بعد از انتشار هر Blue باید حداقل یک Reaction سالم کامل بدون Blue بگذرد. پیامدها:

- Reaction حامل scale، Reset خودش را برای Blue جداگانه space نمی‌کند.
- scale سرکوب‌شده به‌دلیل spacing هنوز strike count مرجع بعدی را به‌روزرسانی می‌کند.
- spacing یک قاعدهٔ stateful است؛ filter سادهٔ خطوط پس از تولید معادل آن نیست.

### 11.5. قیمت و بازهٔ scale Blue

در decisive candle:

```text
price = Low + (High - Low) / 3
```

بازهٔ خط:

```text
from = source_time - timeframe
to   = source_time + timeframe
```

### 11.6. Reset Blue

Reset candidateها با `from_first_idx` گروه‌بندی می‌شوند. برای روند صعودی:

```text
price = resetCandle.Low + (resetCandle.High - resetCandle.Low) / 5
```

Blue از نوع Reset روی main candle Reset و با broken level/provenance همان Reset ساخته می‌شود و spacing lock را رعایت می‌کند.

### 11.7. calculation_valid

یک Reset Blue ممکن است ساخته شود ولی `calculation_valid = false` بگیرد؛ از جمله وقتی Blue قبلی دقیقاً روی reset index stop شده و Reset Low از extreme منبع آن پایین‌تر است. این line ممکن است برای provenance داخلی وجود داشته باشد، اما A فقط Blueهای `calculation_valid` را مصرف می‌کند و serialization نیز نامعتبرها را کنار می‌گذارد.

ordinal Blue پیش از حذف نامعتبرها تعیین می‌شود؛ بنابراین gap در ordinal خروجی ممکن است صحیح باشد.

## 12. stop یک Blue Line

هر Blue زمان formation دقیق دارد:

- scale Blue در second تأییدکنندهٔ owning Reaction موجود است.
- Reset Blue در first lower second که `broken_level` را strict می‌شکند موجود می‌شود.

برای Reset Blue، scan stop از main candle بعدی آغاز می‌شود:

```text
stopScanStart = source_time + timeframe
```

برای روند صعودی:

```text
BlueStop = اولین lower second با Low < sourceExtreme
```

`Low == sourceExtreme` stop نیست. lower data بر main candle approximation مقدم است.

## 13. ماژول A صعودی

### 13.1. ورودی و اصل pairing

A فقط Blue stateهای معتبر را به‌ترتیب formation مصرف می‌کند. مبنای عادی، pairهای مجاور Blue معتبر است. A با دیدن صرف دو Blue ساخته نمی‌شود؛ ابتدا trigger مربوط به توقف آن‌ها و سپس Reaction تأییدکننده لازم است.

### 13.2. سه مسیر trigger عادی

#### مسیر 1: inherited stop از Reaction روند

اگر یک Reaction صعودی پس از formation Blue قبلی آغاز شود و پیش از formation Blue فعلی break کند:

- continuation level کمترین Low از formation قبلی تا break آن Reaction است.
- از formation Blue فعلی به بعد، اولین `Low < continuationLevel` trigger است.

#### مسیر 2: Blue قبلی پیش از پیدایش Blue فعلی stop شده است

- کمترین Low از event دقیق stop قبلی تا درست پیش از source Blue فعلی freeze می‌شود.
- remainder همان formation candle فعلی برای `Low < frozenLow` بررسی می‌شود.
- اگر آنجا trigger نشود، Blue فعلی نیز باید stop شود و بعد strict low پایین‌تری trigger را بسازد.

#### مسیر 3: هر دو Blue هم‌زمان موجود بوده‌اند

- اولین stop از نظر chronology مشخص می‌شود.
- extreme همان first-stop event continuation level است.
- پس از stop دوم، `Low < firstStopExtreme` لازم است.
- اگر هر دو stop در یک exact event رخ دهند، trigger می‌تواند همان‌جا فوری باشد.

در هر سه مسیر، pair با formation Blue معتبر بعدی منقضی می‌شود و حق ندارد بی‌نهایت در آینده trigger بسازد.

### 13.3. Reaction تأییدکنندهٔ A

بعد از trigger:

- اولین Reaction صعودی انتخاب می‌شود که confirmation دقیقش قبل از trigger نباشد.
- First آن Reaction نباید قبل از بیشینهٔ زمان stopهای لازم برای pair باشد.
- chronology دقیق رعایت می‌شود؛ برابر بودن main index به‌تنهایی کافی نیست.

### 13.4. قیمت و منبع A در کد فعلی

کد فعلی `_a_source` برای Bullish کمترین Low را در بازهٔ زیر انتخاب می‌کند:

```text
trigger_index .. confirmingReaction.break_idx   (inclusive)
```

در tie، منبع زودتر حفظ می‌شود. این نکته مهم است، زیرا توصیف‌های قدیمی که source را فقط تا پیش از First محدود می‌کنند با کد فعلی `TradingBot` برابر نیستند.

پس از emit شدن A، cycle تا break Reaction تأییدکننده جلو می‌رود تا همان داده دوباره مالک A بعدی نشود.

### 13.5. مسیر special double-stop

Blue نامعتبرِ میان Blueهای معتبر می‌تواند special candidate بسازد، اگر:

1. Blue معتبر قبلی وجود داشته باشد.
2. Blue نامعتبر در window مربوطه formation داشته باشد.
3. source/formation candle آن strict از source extreme Blue قبلی عبور کند.
4. اولین Reaction معتبر بعد از trigger پیدا شود.

سپس A با همان source logic ساخته می‌شود. کنترل‌های جلوگیری از تکرار:

- اگر A عادی همان Reaction را مصرف کرده باشد، special حذف می‌شود.
- اگر آخرین A قبلی در همان lifecycle Blue stop شده باشد، candidate خاص می‌تواند سرکوب شود.
- خروجی نهایی با `source_time` و سپس `trigger_event_time` مرتب می‌شود.

## 14. stop و ownership ماژول A

برای A صعودی:

```text
AStop = اولین lower second بعد از confirmation دقیق A با Low < A.price
```

- equality stop نیست.
- اگر A بعدی پیش از stop قبلی تأیید شود، قبلی برای ساخت S معتبر نیست.
- شرط کد سخت‌گیرانه است: stop قبلی باید از confirmation A بعدی زودتر باشد؛ `stop >= nextConfirmation` رد می‌شود.

هر A stop‌شده فوراً یک ownership window می‌سازد، حتی اگر هیچ Order یا S بعداً پیدا نشود. Aهای بعدی که source event آن‌ها داخل window باز باشد برای همان مالکیت واجد شرایط نیستند. window پس از source یک S موفق به‌اندازهٔ یک timeframe بسته می‌شود؛ اگر S ساخته نشود، pending ownership باز می‌ماند.

## 15. Order در روند صعودی

در روند صعودی:

```text
trend direction = bullish
order direction = bearish
```

Order یک Reaction نزولی یا geometry نزولی معادل آن است. شرح کامل روند نزولی موضوع این سند نیست، اما فیلدهای Order برای S/E چنین‌اند:

- First index/time
- Break index/time و confirmation exact time
- reaction mode/number
- stop level و source آن
- stop hit index/time و exact event
- cause یا causeهای مالکیتی

### 15.1. اولین Order عادی برای S

اولین Reaction نزولی انتخاب می‌شود که:

```text
order.First main time > exact A-stop event
و
order.confirmation exact time > exact A-stop event
```

### 15.2. stop level Order نزولی

برای Bearish Mode A:

- اول `anchor_value` و در نبود آن `leg_boundary`.
- source همان anchor است یا با جست‌وجوی boundary پیدا می‌شود.

برای Bearish Mode B:

- stop level از `BoxTop` Reaction نزولی قبلی می‌آید.
- source نیز source همان BoxTop است.
- reaction number یک یا کمتر برای این مسیر خطای ساختاری است.

stop Order نزولی:

```text
اولین High > orderStopLevel
```

تساوی stop نیست.

## 16. ماژول S صعودی

### 16.1. ورودی‌ها

S صعودی از این داده‌ها استفاده می‌کند:

- Aهای صعودی مرتب‌شده بر اساس reaction break و source.
- Reactionهای صعودی برای confirmation/containment.
- Reaction و Reset نزولی برای Order.
- main و lower candles برای race دقیق.

### 16.2. تعیین pre-order candidate

مقایسهٔ `order.BoxBottom` با Low کندل A-stop تعیین می‌کند candidate نسبت به stop چگونه تفسیر شود:

```text
orderBoundary <= aStopExtreme  => candidateAfter
orderBoundary >  aStopExtreme  => candidateBefore
```

pre-order candidate صعودی کمترین Low را از remainder دقیق A-stop و سپس main candleهای بعدی تا First Order می‌گیرد. event دقیق پایین‌ترین lower second نیز نگه داشته می‌شود. در تساوی، helper این مسیر provenance زودتر را حفظ می‌کند.

### 16.3. advanced candidate

advanced path یک Reaction صعودی را می‌خواهد که:

- از نظر زمانی داخل Order نزولی nested باشد.
- از نظر price کاملاً داخل box Order باشد.
- boundary منبع آن برای Bullish از `order.BoxBottom` می‌آید.

### 16.4. simple candidate

اگر advanced معتبر پیدا نشود، اولین Reaction صعودی که بعد از confirmation Order تأیید می‌شود مبناست. candidate price کمترین Low از Order Break تا Bullish Reaction Break به‌صورت inclusive است. در این helper، equality آخرین candle را برنده می‌کند.

### 16.5. fallback candidate پس از Order

اگر pre-order candidate وجود نداشته باشد، `_candidate_after_order` از remainder exact confirmation Order تا First Reaction روند جست‌وجو می‌کند و anchor زمانی پس از confirmation را رعایت می‌کند.

### 16.6. race تصمیم S

پس از confirmation Order، lower seconds scan می‌شوند:

```text
candidateCross = Low < candidatePrice
orderStop      = High > orderStopLevel
```

candidateCross فقط در/بعد از `candidate_start` معتبر است.

نتیجه:

1. اگر candidateCross و orderStop در یک finest candle باشند، S ساخته نمی‌شود.
2. اگر orderStop زودتر باشد، S قرمز ساخته می‌شود.
3. اگر candidateCross زودتر باشد، S آبی فقط با evidence مجاز ساخته می‌شود.

evidence لازم برای S آبی یکی از این‌هاست:

- Reset Blue هم‌تراز تا زمان event وجود داشته باشد.
- یا یک Reaction عادی صعودی پس از شروع behavior و حداکثر تا event تأیید شده باشد.

اگر pre-order candidate بدون evidence عبور کند، کد آن fallback را کنار می‌گذارد و advanced/simple را ادامه می‌دهد؛ نباید همان candidate نامعتبر بعداً دوباره مصرف شود.

### 16.7. قیمت، source و زمان S

S provenance کامل والد A و Order را نگه می‌دارد. `source_time` محل خط/برچسب، و `decision_event_time` زمان دقیق تصمیم race است. این دو الزاماً برابر نیستند.

رنگ معنای lifecycle دارد:

- Blue: candidate boundary پیش از stop Order و با evidence شکسته شده است.
- Red: Order پیش از candidate stop شده است.

## 17. S نوع 3

Type 3 از A-stop تا قبل از confirmation اولین Order نزولی بعد از stop بررسی می‌شود.

### 17.1. ownerهای واجد شرایط

- Reaction نزولی باید پیش از A-stop تأیید شده باشد.
- نباید تا A-stop Reset شده باشد.
- برای هر Reset نزولی بعدی، leg از Break owner نزولی تا main candle Reset به‌صورت inclusive ساخته می‌شود.

### 17.2. boundary و trigger

برای روند صعودی:

- boundary کمترین Low leg است.
- در tie آخرین candle برنده است.
- پس از Reset باید `Low < boundary` پیش از deadline رخ دهد.
- حداقل یک Reaction صعودی باید بعد از A-stop و حداکثر تا cross تأیید شده باشد.
- earliest decision برنده است.

### 17.3. خروجی Type 3

- Order metadata مصنوعی ساخته نمی‌شود.
- `formation_type = "type3"`.
- در کد فعلی S نسخه 4.1.1 رنگ Type 3 همیشه blue است؛ برای روند صعودی نیز Blue است.
- UI هم Type 3 را بدون اختراع Order geometry یا stop آن رسم می‌کند.

## 18. ماژول E صعودی

### 18.1. نقش E

E زنجیرهٔ بعد از stop شدن S یا E قبلی را با مصرف Orderهای نزولی می‌سازد. E هم geometry و هم lifecycle Order را مدیریت می‌کند. برای یافتن اولین strict crossing از ساختار `_CrossIndex` مبتنی بر segment tree استفاده می‌شود؛ جایگزینی آن با scan متفاوت فقط وقتی مجاز است که parity کامل حفظ شود.

### 18.2. stop والد

برای والد صعودی S یا E:

```text
parentStop = اولین lower second با Low < parent.price
```

scan از decision exact والد به بعد است. Order نزولی نیز با `High > stopLevel` متوقف می‌شود.

### 18.3. علت‌های Order

یک geometry فیزیکی Order می‌تواند یک یا چند cause داشته باشد:

- `parent-stop`: Order_A مستقیم پس از stop والد.
- `reset-leg`: Order_B از leg یک Reset نزولی.
- `carried-live`: label eligibility برای Order زندهٔ قبلی؛ geometry جدید نیست.

Identity فیزیکی عمدتاً با `(FirstIndex, BreakIndex)` تعیین می‌شود. اگر دو cause به یک identity برسند، ادغام می‌شوند؛ دو رأی یا دو وزن مستقل ایجاد نمی‌شود.

### 18.4. Order_A مستقیم

- بعد از exact parent stop از API مستقیم Reaction گرفته می‌شود.
- Firstی که پیش از exact event باز شده باشد نباید به stop جدید نسبت داده شود.
- race gate/owner با lower seconds حل می‌شود.
- Order هم‌main-candle که توسط A اولیه مالک شده است می‌تواند مسیرهای nested بعدی را block کند.

### 18.5. Order_B از reset-leg

برای هر owner/reset نزولی:

1. leg از owner Break تا Reset main candle inclusive است.
2. boundary صعودی کمترین Low leg است.
3. بعد از Reset، `Low < boundary` gate را باز می‌کند.
4. leg باید حداقل یک confirmation Reaction صعودی از شروع leg تا boundary cross داشته باشد.
5. geometry نزولی بعدی با حفظ context Reset و gate position ساخته می‌شود.

اگر owner نزولی پیش از gate فعال باشد، nested Order_B تا Reset همان owner block می‌شود. Reset روند صعودی این owner مخالف را آزاد نمی‌کند.

For bullish leg ownership, an invalid leg head with a pending S candidate keeps
the internal window through its exact strict stop. An opposite-Reaction First
opened during that interval cannot become the Order_B of the resumed outer E
space. Selection resumes after the head stop. An invalid head with no pending S
candidate does not block an unrelated Order_B.

### 18.6. candidate pool و deadline

- pool مستقیم و reset-leg ساخته می‌شود.
- identityهای برابر و causeها merge می‌شوند.
- stop/cross هر Order محاسبه می‌شود.
- deadline موقت، زودترین stop شناخته‌شدهٔ مرتبط است.
- فقط Orderهایی که تا decision deadline تأیید شده‌اند حق رقابت دارند.
- مرتب‌سازی اولیه بر اساس stop event و سپس First است.

در انتخاب نهایی `_zone` کلید مؤثر شامل این معناست:

```text
(stopEvent, -first_idx)
```

پس در stop event برابر، Order جدیدتر با `first_idx` بزرگ‌تر ترجیح می‌گیرد.

### 18.7. carry کردن Order زنده

Order می‌تواند از یک parent به parent بعدی منتقل شود، اما duplicate نمی‌شود.

- S آبی می‌تواند Order مصرف‌نشده را carry کند اگر stop آن در/بعد از stop S باشد.
- Order accepted ledger اگر داخل عمر parent ساخته، پیش از parent stop تأیید، و در/بعد از parent stop متوقف شده باشد، eligible است.
- Order اولیهٔ متعلق به gate A که در همان main candle parent stop شروع و پس از exact stop confirm می‌شود، می‌تواند nested direct بعدی را block کند.

### 18.8. source قیمت E

برای Bullish، source E کمترین Low در این بازه است:

```text
main candle حاوی parent stop .. main candle حاوی order stop   (inclusive)
```

در tie منبع زودتر حفظ می‌شود. decision E برابر بیشینهٔ exact parent stop و exact order stop است؛ در مسیر معمول، order stop دیرتر و بنابراین decision نهایی است.

### 18.9. بازگشت recursive

برای هر S:

1. E1 موقت ساخته می‌شود.
2. اگر E1 با strict low متوقف شود، همان منطق برای E2 اجرا می‌شود.
3. زنجیره تا نبود parent stop یا Order معتبر ادامه پیدا می‌کند.
4. زنجیره‌های تمام Sها سپس با chronology و active-state reconcile می‌شوند.

### 18.10. family، number و dominance

اولویت sequence:

```text
E red  = 4
S red  = 3
E blue = 2
S blue = 1
```

قواعد اصلی:

- E متوقف‌شده از active set حذف می‌شود ولی historical record باقی می‌ماند.
- family از والد پذیرفته‌شده به ارث می‌رسد.
- Red بر Blue غالب است.
- number برابر بیشترین number از active stoppedهای همان family به‌علاوهٔ یک است؛ اگر وجود نداشته باشد 1.
- یک S قرمز منفرد می‌تواند طی Eهای آبی nested همچنان dominance خود را حفظ کند.
- StopAll sequence reset در source خودش state فعال E را پاک و شماره‌گذاری بعدی را restart می‌کند.
- parent child بعد از boundary می‌تواند با `parent_type = StopAll` برچسب بخورد.

### 18.11. rebuild ممیزی E

پس از حل accepted S/E/StopAll، order audit دوباره فقط از والدهای پذیرفته‌شده ساخته می‌شود. Order برندهٔ یک E پذیرفته‌شده اجباراً در ledger نهایی حفظ می‌شود و causeهای Reset/parent به آن افزوده می‌شوند.

### 18.12. helperهای غیرمسیر اصلی E

وجود این helperها دلیل بر اجرای runtime آن‌ها نیست:

- `_strict_stop` در مسیر optimized اصلی مستقیماً استفاده نمی‌شود.
- `_is_reset_leg_order` در call path اصلی جاری نیست.
- `_order_cause_evidence` عمدتاً مصرف آزمون دارد.
- `visual_order_lifecycle` و `_active_prior_order` مسیر ارائه/قدیمی‌اند و مبنای ledger authoritative فعلی نیستند.

## 19. StopAll صعودی

### 19.1. ورودی و محدودیت

StopAll نسخه 1.3.0 خودش Reaction یا Order جدید کشف نمی‌کند. ورودی آن Sهای visible و Eهای accepted است. Order برنده و lineage را از Eای می‌گیرد که باعث تشکیل StopAll شده است.

### 19.2. priority گروهی

priority داخلی StopAll:

```text
S blue = 1
E blue = 2
S red  = 3
E red  = 4
```

هویت group:

- برای S: رنگ دقیق.
- برای E: زوج دقیق `(family, number)`.

### 19.3. ترتیب پردازش

Eها به‌ترتیب source پردازش می‌شوند. پیش از هر E، فقط Sهایی مصرف می‌شوند که:

```text
S.source_time < currentE.source_time
```

برابری زمان، S را پیش از آن E مصرف نمی‌کند.

### 19.4. active group

- event با priority بالاتر active group را جایگزین می‌کند.
- S هم‌رنگ در غیاب E فعال count را افزایش می‌دهد.
- E با family/number یکسان count را افزایش می‌دهد.
- E قرمز بر Blue غالب است، مستقل از number.
- در family یکسان، E با number بالاتر group را جلو می‌برد.
- event با priority پایین‌تر ممکن است در خروجی تاریخی بماند، اما group dominant را جدا نمی‌کند.

### 19.5. شرط تشکیل StopAll1

پیش از integrate کردن E جاری، اگر active group حداقل دو عضو هم‌گروه داشته باشد:

1. آخرین عضو قبلی matching پیدا می‌شود.
2. strict stop آن پس از decision خودش محاسبه می‌شود.
3. اگر stop gate آن حداکثر تا decision E جاری رخ داده باشد، E جاری به StopAll1 تبدیل می‌شود.
4. Order، source و lineage همان E جاری حفظ می‌شود.
5. group state reset می‌شود.

برای روند صعودی strict stop عضو قبلی `Low < price` است.

### 19.6. ادامهٔ StopAll

پیش از group logic، active StopAllها بررسی می‌شوند. اگر یک یا چند StopAll active تا decision E جاری strict-stop شده باشند:

```text
newStopAll.number = max(stoppedActiveStopAll.number) + 1
```

E جاری به StopAll بعدی تبدیل، StopAllهای متوقف از active set حذف و sequence group reset می‌شود.

هر StopAll تکمیل‌شده خودش metadata stop بعدی را می‌گیرد تا continuation بعدی قابل تشخیص باشد.

### 19.7. lineage StopAll

StopAll:

- color مستقل ندارد.
- Order geometry/cause E برنده را حمل می‌کند.
- family و number زیرین E را برای audit نگه می‌دارد.
- `source_time` آن boundary reset برای E sequence numbering است.

## 20. reconcile حلقه‌ای E و StopAll

bridge یک fixed-point reconciliation اجرا می‌کند:

```text
repeat:
    visibleS  = filter S after current E/reset boundaries
    stopAlls  = detect StopAll(visibleS, currentE)
    resets    = {stopAll.source_time: stopAll.number}

    if resets == EDetector.sequence_resets:
        stable => return currentE, stopAlls

    if reset identity قبلاً دیده شده:
        error: reconciliation did not converge

    EDetector.sequence_resets = resets
    currentE = rerun E with same geometry/ledger inputs
```

این حلقه باید به نقطهٔ ثابت برسد. cycle به‌عنوان خطا raise می‌شود؛ bridge نباید یک payload نیمه‌اصلاح‌شده منتشر کند.

پیش از این حلقه نیز E چند بار ساخته می‌شود:

1. E اولیه با S اولیه.
2. مالکیت Sها بر اساس exact stop رفتار غالب و شکست strict مرز قیمت آن حل می‌شود؛ برابری قیمت شکست محسوب نمی‌شود.
3. در صورت تغییر، E با S فیلترشده و زمان اولین Orderهای blocked دوباره ساخته می‌شود.
4. A sourceهای پذیرفته و S order audit پالایش می‌شوند.
5. E برای final audit دوباره instantiate می‌شود.

## 21. visibility و مالکیت نهایی

بعد از reconcile:

1. Eای که source آن دقیقاً source یک StopAll است از E visible حذف می‌شود؛ StopAll نمایندهٔ نهایی آن event است.
2. وجود هر Reaction هم‌جهت معتبر همچنان می‌تواند Blue Line و زنجیرهٔ پایهٔ `A -> S` بسازد؛ وجود رفتار بزرگ‌تر این محاسبات نیم‌لگ را خاموش نمی‌کند.
3. اگر parent A یک S candidate متوقف شده باشد، رفتار غالب قبلی نیز تا exact event استاپ A متوقف شده باشد و قیمت S جدید به‌صورت strict پایین‌تر از مرز رفتار غالب باشد، آن S candidate به‌عنوان گذار به lifecycle بزرگ‌تر مصرف می‌شود. برابری یا قیمت بالاتر، این گذار را فعال نمی‌کند.
4. رفتار غالب با ترتیب `StopAll > E red > S red > E blue > S blue > A` تعیین می‌شود. استاپ هم‌زمان رفتارهای کوچک‌تر، مالکیت رفتار غالب را تغییر نمی‌دهد؛ برای نمونه استاپ E2 همراه S/A وارد فضای E3 می‌شود، نه E1.
5. ابتدای مقایسه، خود main candle حاوی exact stop است. فقط کندلی که واقعاً یک رفتار تشخیص‌داده‌شده دارد می‌تواند `LegStart` جدید شود؛ یک low خامِ بدون رفتار، مالکیت leg را جابه‌جا نمی‌کند.
6. در Bullish، اگر قیمت رفتار کاندید روی `LegStart` به‌صورت strict از قیمت رفتار غالب پایین‌تر باشد، رفتار مساوی یا کوچک‌تر اجازهٔ ورود به محاسبات downstream را ندارد. اگر دو low برابر باشند، low اول مالک است و مورد دوم strict break نیست.
7. Rejected A/S candidates remain available only to internal lifecycle calculations. They are absent from the public payload and cannot create chart labels, object-tree entries, counts, or order geometry. Published A/S objects are calculation-valid.
8. رفتارهای معتبرِ متوقف‌شده و شکل‌هایشان در payload و chart باقی می‌مانند، ولی پس از انتقال مالکیت دیگر در چرخهٔ بعدی مصرف نمی‌شوند.
9. تمام شرط‌ها برای Bearish آینهٔ دقیق‌اند: به‌جای `price < boundary` از `price > boundary` استفاده می‌شود.
10. collisionها با priority نهایی حل می‌شوند:

```text
StopAll > E > S > A
```

این priority برای یک source/جایگاه مشترک است. حذف از view به معنی انکار lineage محاسباتی object پایین‌دستی نیست.

پس از حل ownership، bridge روی خروجی نمایشی lineage closure اجرا می‌کند: هر S پذیرفته‌شده‌ای که یک E نهایی با `parentType = S` و `parentSourceTime` متناظر صریحاً به آن ارجاع می‌دهد، در `sZones` نمایشی حفظ می‌شود؛ سپس A والد هر S نهایی نیز با `aSourceTime` در `aZones` حفظ می‌شود. این بازگردانی فقط برای parent واقعی یک خروجی پایین‌دستی است؛ candidate انتقالی که هیچ child نهایی ندارد دوباره وارد نمایش نمی‌شود.

## 22. Order Audit

Order audit از دو منبع merge می‌شود:

- audit اولیهٔ S برای Orderهای والد A.
- accepted ledger ماژول E.

کلید identity:

```text
(FirstIndex, BreakIndex)
```

برای یک identity واحد، causeها ادغام و deduplicate می‌شوند.

cause نوع `parent-stop` می‌تواند شامل این‌ها باشد:

- parent type: A، S، E یا StopAll.
- parent family.
- exact stop event.
- parent source.

cause نوع `reset-leg` شامل reset و boundary break مربوطه است.

فیلدهای اصلی هر رکورد:

- `direction = "bearish"` برای audit خروجی Bullish.
- reaction number؛ برای Order_B مصنوعی ممکن است صفر باشد.
- reaction mode.
- First index/time.
- BoxTop و source index/time آن.
- BoxBottom و source index/time آن.
- Break index/time.
- stop level و stop source.
- stop hit index/main time/exact event.
- آرایهٔ causeها.

فقط Orderهایی که First index آن‌ها داخل start/end presentation range باشد serialize می‌شوند. ترتیب نهایی بر اساس First و Break است.

`orderAudit` هم خروجی ممیزی و هم منبع کامل هندسهٔ Order است. chart ابتدا Orderهای متصل به S/E/StopAll را رسم می‌کند و سپس هر audit معتبرِ باقی‌مانده را که با identity `(FirstIndex, BreakIndex)` قبلاً رسم نشده است، به‌صورت مستقل نمایش می‌دهد. به این ترتیب یک Order فیزیکی دوبار رسم نمی‌شود ولی هیچ Order معتبر محاسبه‌شده‌ای نیز صرفاً به‌دلیل نداشتن label نهایی S/E/StopAll گم نمی‌شود. نمایش مستقل audit فقط شامل Box سفارش است؛ خط توقفِ audit-only رسم نمی‌شود و خطوط توقف Order فقط از S/E/StopAll می‌آیند.

## 23. قرارداد JSON خروجی Bullish

payload جهت صعودی این collectionها را دارد:

```text
reactions
resets
blueLines
aZones
sZones
eZones
stopAlls
orderAudit
```

### 23.1. envelope اصلی

bridge در سطح ریشه این metadata را می‌فرستد:

```text
engine
version
blueLineVersion
aVersion
sVersion
eVersion
stopAllVersion
blueLinesEnabled
aEnabled
sEnabled
eEnabled
stopAllEnabled
timeframe
actualFrom
actualTo
directions
```

خروجی این سند داخل `directions.bullish` قرار می‌گیرد. `actualFrom` و `actualTo` زمان اولین و آخرین main candle واقعاً انتخاب‌شده‌اند و ممکن است برای تشخیص دقیق بازه از from/to درخواستی مفیدتر باشند.

### 23.2. فیلدهای دقیق `reactions`

```text
firstIndex
firstTime
boxTopSourceIndex
boxTopSourceTime
boxTop
boxBottomSourceIndex
boxBottomSourceTime
boxBottom
breakIndex
breakTime
mode
```

`breakTime` در این collection زمان main candle است؛ زمان‌های exact lower-second عمدتاً در objectهای lifecycle پایین‌دستی نگه داشته می‌شوند.

### 23.3. فیلدهای دقیق `resets`

```text
index
time
secondTime
brokenLevel
fromFirstIndex
```

`time` زمان main candle و `secondTime` زمان دقیق lower-second است؛ اگر exact second موجود نباشد مقدار دوم می‌تواند null باشد.

### 23.4. فیلدهای دقیق `blueLines`

```text
direction
kind
reactionNumber
previousStrikeCount
strikeCount
fibonacciLevel
sourceIndex
sourceTime
sourceExtreme
brokenLevel
linePrice
startTime
endTime
```

فقط itemهایی serialize می‌شوند که `calculation_valid` آن‌ها false نباشد.

### 23.5. فیلدهای دقیق `aZones`

```text
direction
blue1Ordinal
blue2Ordinal
blue1SourceTime
blue2SourceTime
blue1StopTime
blue2StopTime
blue1StopLevel
blue2StopLevel
continuationLevel
continuationSourceIndex
continuationSourceTime
triggerIndex
triggerTime
triggerEventTime
reactionNumber
reactionFirstTime
reactionBreakTime
sourceIndex
sourceTime
price
```

`triggerTime` main time و `triggerEventTime` exact time است.

### 23.6. فیلدهای دقیق `sZones`

```text
direction
color
formationType
aOrdinal
aSourceIndex
aSourceTime
aPrice
aStopIndex
aStopTime
aStopEventTime
orderDirection
orderReactionNumber
orderMode
orderFirstIndex
orderFirstTime
orderBreakIndex
orderBreakTime
orderConfirmationTime
orderBoxTop
orderBoxTopSourceIndex
orderBoxTopSourceTime
orderBoxBottom
orderBoxBottomSourceIndex
orderBoxBottomSourceTime
orderStopLevel
orderStopSourceIndex
orderStopSourceTime
resetReactionNumber
resetTime
sourceIndex
sourceTime
price
decisionIndex
decisionTime
decisionEventTime
```

در Type 3 فیلدهای Order می‌توانند null باشند؛ مصرف‌کننده نباید geometry خیالی بسازد.

### 23.7. فیلدهای دقیق `eZones`

```text
direction
family
number
parentType
parentSourceIndex
parentSourceTime
parentPrice
parentStopIndex
parentStopTime
parentStopEventTime
orderDirection
orderReactionNumber
orderMode
orderCauses
orderParentStopCauseTime
orderResetLegResetTime
orderResetLegBreakTime
orderFirstIndex
orderFirstTime
orderBreakIndex
orderBreakTime
orderConfirmationTime
orderBoxTop
orderBoxTopSourceIndex
orderBoxTopSourceTime
orderBoxBottom
orderBoxBottomSourceIndex
orderBoxBottomSourceTime
orderStopLevel
orderStopSourceIndex
orderStopSourceTime
sourceIndex
sourceTime
price
decisionIndex
decisionTime
decisionEventTime
```

`orderCauses` یک list از labelهای cause است؛ زمان‌های اختصاصی cause نیز در سه فیلد جداگانه حفظ می‌شوند.

### 23.8. فیلدهای دقیق `stopAlls`

```text
direction
number
sourceIndex
sourceTime
price
decisionIndex
decisionTime
decisionEventTime
gateType
gateEventTime
stoppedBehaviorType
stoppedBehaviorKey
stoppedBehaviorCount
underlyingEFamily
underlyingENumber
orderDirection
orderReactionNumber
orderMode
orderCauses
orderParentStopCauseTime
orderResetLegResetTime
orderResetLegBreakTime
orderFirstIndex
orderFirstTime
orderBreakIndex
orderBreakTime
orderConfirmationTime
orderBoxTop
orderBoxTopSourceIndex
orderBoxTopSourceTime
orderBoxBottom
orderBoxBottomSourceIndex
orderBoxBottomSourceTime
orderStopLevel
orderStopSourceIndex
orderStopSourceTime
stopIndex
stopTime
stopEventTime
```

`stopTime` main time و `stopEventTime` exact lower-second time توقف خود StopAll است و تا وقتی StopAll متوقف نشده باشد null می‌مانند.

### 23.9. فیلدهای دقیق `orderAudit`

```text
direction
reactionNumber
reactionMode
firstIndex
firstTime
boxTopSourceIndex
boxTopSourceTime
boxTop
boxBottomSourceIndex
boxBottomSourceTime
boxBottom
breakIndex
breakTime
stopLevel
stopSourceIndex
stopSourceTime
stopHitIndex
stopHitTime
stopHitEventTime
causes
```

شکل cause نوع parent-stop:

```text
kind
parentType
parentFamily
eventTime
parentSourceTime
```

شکل cause نوع reset-leg:

```text
kind
resetTime
boundaryBreakTime
```

قواعد serialization:

- زمان‌ها: Unix epoch second متناظر با `Asia/Tehran` داخلی.
- قیمت Decimal: رشته.
- indexها و ordinal/numberها: integer.
- mode، family، color، formationType و parentType: رشته‌های معنایی.
- source و decision هر object جدا نگه داشته می‌شوند.
- provenance Order داخل S/E/StopAll جایگزین orderAudit نیست؛ هر دو برای هدف متفاوت وجود دارند.

bridge از stdout فقط JSON نهایی را می‌فرستد. progress روی stderr با prefix مخصوص گزارش می‌شود تا stdout خراب نشود.

## 24. رفتار مرورگر و موارد غیرمحاسباتی

`main.js` payload را به objectهای رسم تبدیل می‌کند:

- Reaction boxها.
- Blue lineها.
- label/line A.
- S و Order همراه آن، اگر Type 3 نباشد.
- E و Order همراه آن.
- StopAll و Order همراه آن.
- stop lineهای deduplicate‌شدهٔ Orderهای متصل به S/E/StopAll؛ audit-only خط توقف نمی‌سازد.

Reset در payload محاسبات و صفحهٔ info باقی می‌ماند، اما chart برای آن object/label قابل‌رسم `R` نمی‌سازد؛ بنابراین تمام لیبل‌های `R` همیشه مخفی هستند.

کلید dedupe stop Order شامل direction، order FirstIndex و order stop source index است.

یک قاعدهٔ صرفاً نمایشی وجود دارد: stop line والد E فقط وقتی رسم می‌شود که `parent_type == E` و فاصلهٔ index میان parent stop و parent source بیش از 350 باشد. این threshold بخشی از محاسبهٔ E نیست.

کاربر می‌تواند visibility، رنگ یا position بعضی objectها را تغییر دهد، اما این overrideها نباید وارد payload محاسباتی یا الگوریتم Python شوند.

در request فعلی UI، `blueLines: true` به API ارسال می‌شود. خاموش‌کردن نمایش Blue با خاموش‌کردن محاسبهٔ upstream یکی نیست.

## 25. شبه‌کد اجرایی کامل

```text
INPUT:
    rawRows, timeframe, fromEpoch, toEpoch, direction="bullish"

VALIDATE:
    exact candle schema
    finite and valid OHLC
    positive safe integer timestamps
    strictly increasing chronology

FILTER RAW:
    keep fromEpoch <= time < toEpoch + timeframe

NORMALIZE:
    convert epoch -> Asia/Tehran local datetime
    Decimal(str(OHLC))
    tag GREEN if Open <= Close else RED

AGGREGATE:
    build 1-second candles
    build timeframe candles
    eligible presentation indices have bucket time in [fromEpoch, toEpoch]

REACTION GEOMETRY:
    bullishReactions, bullishResets = UnifiedReactionDetector(bullish)
    bearishReactions, bearishResets = UnifiedReactionDetector(bearish)

BLUE:
    bullishBlueStates = detect_blue_lines(
        bullishReactions,
        bullishResets,
        mainCandles,
        secondCandles
    )

A:
    bullishA = detect_a_zones(
        valid bullishBlueStates,
        bullishReactions,
        mainCandles,
        secondCandles
    )

S:
    bullishS, initialOrderAudit = SDetector.detect(
        bullishA,
        bullishReactions,
        bearishReactions as Orders,
        bearishResets,
        blue states,
        mainCandles,
        secondCandles
    )

E INITIAL:
    bullishE = EDetector.detect(
        bullishS,
        bullishA,
        bullishReactions,
        bearish reaction geometry APIs,
        bearishResets,
        initial order ledger,
        mainCandles,
        secondCandles
    )

S RECONCILIATION:
    remove S made stale by accepted module reset boundaries
    if changed:
        rerun E with filtered S and blocked-order provenance

FINAL AUDIT PASS:
    filter accepted A sources
    rebuild S order audit
    rerun E so accepted ledger matches accepted parents

FIXED-POINT STOPALL:
    do:
        visibleS = resolve S by dominant exact-stop ownership
        stopAlls = detect_stopalls(visibleS, bullishE)
        resets = map stopAll.source_time -> stopAll.number
        if resets stable: break
        if cycle: raise error
        rerun E with sequence_resets = resets

FINAL OWNERSHIP:
    suppress E represented by StopAll at same source
    map every exact stop to its containing main candle
    allow only a detected-behavior candle to become the next LegStart
    reject equal/lower A at a strict new directional extreme
    consume would-be S only when both stop chronology and strict price break hold
    retain rejected candidates only in internal lifecycle state
    exclude rejected objects from S/E/StopAll and order-audit inputs
    apply StopAll > E > S > A collision ownership

SERIALIZE:
    only selected presentation range
    omit every calculation-invalid behavior
    Decimal -> string
    Tehran datetime -> epoch second
    output reactions/resets/blueLines/aZones/sZones/eZones/stopAlls/orderAudit
```

## 26. قواعد الزامی برای پیاده‌سازی یا اصلاح توسط هوش مصنوعی دیگر

1. کد فعلی `TradingBot` مرجع رفتار است؛ متن `Prj-1` فقط شاهد کمکی است.
2. برای خروجی Bullish، Bearish Reaction/Reset را حذف نکن؛ آن‌ها Order authority هستند.
3. هیچ timestamp، OHLC fingerprint، dataset-specific branch یا خروجی دستی hardcode نشود.
4. تمام قیمت‌ها Decimal بمانند و serialization آن‌ها رشته باشد.
5. strict crossingها به `>=` یا `<=` تبدیل نشوند.
6. raceهای داخل یک main candle با lower seconds حل شوند.
7. exact event time و main source time با هم یکی فرض نشوند.
8. owner، source، decision، parent و cause provenance حذف نشوند.
9. equality tie هر helper بدون بررسی کد همان helper تغییر نکند.
10. browser هیچ قاعدهٔ محاسباتی را دوباره نسازد.
11. ترتیب pipeline یا feedback StopAll به E با یک pass ساده جایگزین نشود.
12. Order causeهای merge‌شده duplicate geometry محسوب نشوند.
13. suppression نمایش با حذف تاریخچه یا ledger اشتباه نشود.
14. helperهای dormant صرف وجودشان وارد specification runtime نشوند.
15. قبل و بعد از هر اصلاح، آزمون‌های unit، integrated، directional symmetry و real-data regression صریح اجرا شوند.
16. هر ادعای parity باید collection-by-collection و field-by-field باشد، نه فقط count یا ظاهر chart.

## 27. وضعیت اعتبارسنجی snapshot حاضر

فرمان compile صریح هفت فایل Python فعال بدون خطا تمام شد.

آزمون‌های Node:

```text
92 passed, 0 failed
```

آزمون‌های Blue صریح:

```text
12 passed, 2 failed
```

شکست‌ها:

```text
test_reset_source_window_uses_extreme_through_first_trend_candle
test_reset_candidate_expires_when_prior_blue_stops_before_formation
```

اجرای یکپارچهٔ A/S/E/StopAll/symmetry با fallback موقت in-memory برای dependency مفقود `orjson`:

```text
196 passed, 3 skipped, 6 failed
```

شکست‌های واقعی مشاهده‌شده:

```text
test_fxcm_parent_s_color_priority_and_same_family_continuation
test_fxcm_user_verified_orders_and_e_through_2026_07_15_221400
test_fxcm_full_file_order_b_active_owner_regression
test_clarified_range_continues_after_stopall_with_exclusive_labels_and_order_causes
test_strict_range_real_order_ledger_is_deterministic_on_repeated_detect
test_full_file_dominant_e_blocks_early_s_and_preserves_stopall_lineage
```

یکی از شکست‌ها cycle در fixed-point E/StopAll و خطای زیر بود:

```text
ValueError: E/StopAll lifecycle reconciliation did not converge
```

آزمون Reaction با fallback in-memory برای `orjson` تا بخش‌های موجود پیش رفت:

- آزمون doji سبز پاس شد.
- 82 آزمون full-output directional mirror و geometry bounded پاس شدند.
- ادامه به‌دلیل نبود فایل legacy runtime در مسیر قدیمی `D:` متوقف شد.

اجرای عادی بخشی از تست‌های bridge بدون fallback به‌دلیل نصب نبودن `orjson` در Python محیط fail می‌شود؛ این failure محیطی با شکست‌های assertion بالا متفاوت است.

build Vite در VMware share با خطای resolve شدن entry path شکست خورد، در حالی که 92 آزمون Node پاس شدند. این مشکل build شاهد تغییر قاعدهٔ محاسباتی نیست.

نتیجهٔ صحیح از این شواهد:

- این سند با call path و رفتار کد snapshot فعلی نوشته شده است.
- سلامت syntax و بخش بزرگی از قراردادها اثبات شده است.
- snapshot فعلی را نباید «تمام آزمون‌ها سبز و business-verified» معرفی کرد.
- پیش از هر تغییر الگوریتمی باید ابتدا مشخص شود شکست‌های ثبت‌شده ناشی از regression کد جدیدند یا expectationهای قدیمی.

## 28. چک‌لیست بازسازی مستقل خروجی Bullish

یک پیاده‌سازی مستقل فقط وقتی معادل است که برای یک ورودی یکسان، این موارد دقیقاً برابر باشند:

- تعداد و تمام فیلدهای Reactionهای صعودی.
- Reset main time، exact second time، broken level و owner.
- Blue type، source، price، ordinal، strike state و validity.
- Blue stop exact chronology.
- A trigger path، source range، parent Blueها و confirming Reaction.
- A stop و ownership windows.
- S formation type، color، candidate path، evidence و race.
- Order First/Break/stop/cause برای S.
- E parent stop، selected Order، carry state، family و number.
- accepted Order ledger و cause merge.
- StopAll number، underlying E lineage و stop lifecycle.
- نتیجهٔ fixed-point sequence resets.
- visibility و collision priority.
- رشتهٔ دقیق Decimal و epoch time نهایی.

مقایسهٔ صرف تصویر chart یا تعداد objectها کافی نیست.

## 29. جمع‌بندی فشردهٔ semantics صعودی

- Reaction صعودی از یک Box با FirstRed، BoxTop و BoxBottom ساخته و با `High > BoxTop` تأیید می‌شود.
- Reset صعودی با `Low < confirmed BoxBottom` رخ می‌دهد.
- Blue از رشد strike count یا Reset معتبر، با spacing stateful ساخته می‌شود.
- A از lifecycle توقف دو Blue و یک Reaction تأییدکننده به‌وجود می‌آید.
- توقف A پنجرهٔ مالکیت S را باز می‌کند.
- S با Order نزولی و race میان candidate low و Order high-stop تعیین می‌شود؛ Type 3 مسیر بدون Order metadata است.
- E پس از stop والد با Order_A، Order_B یا carried-live Order زنجیره می‌سازد.
- dominance دقیق Red/Blue و family/number state E را تعیین می‌کند.
- StopAll از ledger مشترک S/E، فقط هنگام پردازش یک E مناسب ساخته می‌شود.
- StopAll boundary دوباره به E بازخورد داده می‌شود تا fixed point حاصل شود.
- خروجی نهایی با ownership `StopAll > E > S > A` serialize می‌شود.

این زنجیره یک سیستم stateful و chronology-sensitive است؛ هیچ مرحله‌ای را نمی‌توان مستقل از provenance مرحلهٔ قبل یا ترتیب lower-second eventها ساده‌سازی کرد.
