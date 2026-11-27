const HOUR = 60;
const DAY_MINUTES = 24 * HOUR;
const DAY_MS = 86_400_000;
const newYorkClock = new Intl.DateTimeFormat("en-US", {
  timeZone: "America/New_York",
  hourCycle: "h23",
  year: "numeric",
  month: "2-digit",
  day: "2-digit",
  hour: "2-digit",
  minute: "2-digit",
});

const forexComMetals = {
  open: 18 * HOUR,
  close: 17 * HOUR,
  source: "https://www.cmegroup.com/markets/metals/precious/gold/specs",
  holidaySource: "https://www.cmegroup.com/trading-hours.html",
  holidays: {
    "2026-11-26": { close: 14 * HOUR + 30 },
    "2026-11-27": { close: 14 * HOUR + 45 },
    "2026-12-24": { close: 13 * HOUR + 45, reopen: false },
    "2026-12-25": { closed: true },
    "2026-12-31": { reopen: false },
    "2027-01-01": { closed: true },
    "2027-03-25": { reopen: false },
    "2027-03-26": { closed: true },
  },
};

const fxcmCommodities = {
  open: 18 * HOUR,
  close: 17 * HOUR,
  fridayClose: 16 * HOUR + 45,
  source: "https://www.fxcm.com/markets/trading-details/trading-hours/",
  holidaySource: "https://www.fxcm.com/markets/help/cfd-trading-what-are-the-cfd-holiday-hours/",
  holidays: {
    "2026-11-26": { close: 14 * HOUR + 30, open: 18 * HOUR },
    "2026-11-27": { close: 14 * HOUR + 45 },
  },
};

const fxcmCrypto = {
  open: 17 * HOUR,
  fridayClose: 16 * HOUR + 55,
  source: "https://www.fxcm.com/markets/trading-details/trading-hours/",
  holidaySource: "https://www.fxcm.com/markets/help/cfd-trading-what-are-the-cfd-holiday-hours/",
  holidays: {
    "2026-11-26": {},
    "2026-11-27": {},
  },
};

const coinbaseSpot = {
  continuous: true,
  source: "https://exchange.coinbase.com/markets",
};

const binanceSpot = {
  continuous: true,
  source: "https://www.binance.com/en/markets/spot_margin-USDT",
};

const profiles = new Map([
  ["FOREXCOM:XAUUSD", forexComMetals],
  ["FOREXCOM:XAGUSD", { ...forexComMetals, source: "https://www.cmegroup.com/markets/metals/precious/silver/specs" }],
  ["FXCM:USOIL", fxcmCommodities],
  ["FXCM:USOILSPOT", fxcmCommodities],
  ["FXCM:XAUUSD", fxcmCommodities],
  ["FXCM:XAGUSD", fxcmCommodities],
  ["FXCM:BTCUSD", fxcmCrypto],
  ["COINBASE:BTCUSD", coinbaseSpot],
  ["BINANCE:BTCUSDT", binanceSpot],
  ["BINANCE:BTCUSDC", binanceSpot],
]);

const normalize = value => String(value ?? "").toUpperCase().replace(/[^A-Z0-9]/g, "");

function profileFor(instrument) {
  const [prefix, ...symbol] = String(instrument?.symbol ?? "").split(":");
  const broker = normalize(instrument?.broker || (symbol.length ? prefix : ""));
  return profiles.get(`${broker}:${normalize(symbol.length ? symbol.join(":") : prefix)}`);
}

function calendarFields(milliseconds) {
  return Object.fromEntries(
    newYorkClock.formatToParts(milliseconds)
      .filter(part => part.type !== "literal")
      .map(part => [part.type, Number(part.value)]),
  );
}

function marketMidnight(milliseconds) {
  const fields = calendarFields(milliseconds);
  return Date.UTC(fields.year, fields.month - 1, fields.day);
}

function sessionInstant(day, minute) {
  const wallTime = day + minute * 60_000;
  let instant = wallTime;
  for (let attempt = 0; attempt < 3; attempt += 1) {
    const fields = calendarFields(instant);
    const localTime = Date.UTC(fields.year, fields.month - 1, fields.day, fields.hour, fields.minute);
    if (localTime === wallTime) return instant;
    instant += wallTime - localTime;
  }
  return instant;
}

function observedDate(year, month, date) {
  const day = Date.UTC(year, month - 1, date);
  const weekday = new Date(day).getUTCDay();
  if (weekday === 0) return day + DAY_MS;
  if (weekday === 6) return day - DAY_MS;
  return day;
}

// Gregorian Easter, used to identify Good Friday as a possible exchange holiday.
function goodFriday(year) {
  const cycle = year % 19;
  const century = Math.floor(year / 100);
  const centuryYear = year % 100;
  const leapCenturies = Math.floor(century / 4);
  const lunarCorrection = Math.floor((century + 8) / 25);
  const dayCorrection = Math.floor((century - lunarCorrection + 1) / 3);
  const moon = (19 * cycle + century - leapCenturies - dayCorrection + 15) % 30;
  const week = (32 + 2 * (century % 4) + 2 * Math.floor(centuryYear / 4) - moon - (centuryYear % 4)) % 7;
  const leap = Math.floor((cycle + 11 * moon + 22 * week) / 451);
  const date = moon + week - 7 * leap + 114;
  return Date.UTC(year, Math.floor(date / 31) - 1, date % 31 + 1) - 2 * DAY_MS;
}

function mayHaveHolidayHours(day, date) {
  const year = date.getUTCFullYear();
  const month = date.getUTCMonth() + 1;
  const weekday = date.getUTCDay();
  const number = date.getUTCDate();
  return day === observedDate(year, 1, 1)
    || day === observedDate(year + 1, 1, 1)
    || day === observedDate(year, 6, 19)
    || day === observedDate(year, 7, 4)
    || day === observedDate(year, 12, 25)
    || day === goodFriday(year)
    || (weekday === 1 && (
      ((month === 1 || month === 2) && number >= 15 && number <= 21)
      || (month === 5 && number >= 25)
      || (month === 9 && number <= 7)
    ))
    || (month === 11 && (
      (weekday === 4 && number >= 22 && number <= 28)
      || (weekday === 5 && number >= 23 && number <= 29)
    ))
    || (month === 12 && (number === 24 || number === 25 || number === 31))
    || (month === 1 && number === 1)
    || (month === 7 && weekday >= 1 && weekday <= 5 && (number === 3 || number === 4));
}

function unverifiedHoliday(profile, day) {
  const date = new Date(day);
  return !Object.hasOwn(profile.holidays, date.toISOString().slice(0, 10)) && mayHaveHolidayHours(day, date);
}

function regularWindows(profile, weekday, holiday) {
  if (holiday?.closed) return [];
  const close = holiday?.close ?? profile.close;
  const open = holiday?.open ?? profile.open;
  if (weekday === 0) return [[open, DAY_MINUTES]];
  if (weekday === 5) return [[0, holiday?.close ?? profile.fridayClose ?? close]];
  if (close === undefined) return [[0, DAY_MINUTES]];
  return holiday?.reopen === false ? [[0, close]] : [[0, close], [open, DAY_MINUTES]];
}

function dailyWindows(profile, day) {
  const date = new Date(day);
  const weekday = date.getUTCDay();
  if (weekday === 6) return { windows: [] };
  if (unverifiedHoliday(profile, day)) return { windows: [], uncertainAt: 0 };
  const holiday = profile.holidays[date.toISOString().slice(0, 10)];
  const windows = regularWindows(profile, weekday, holiday);
  // The holiday trade date can begin on the preceding evening.
  if (weekday <= 4 && !holiday && unverifiedHoliday(profile, day + DAY_MS)) {
    const uncertainAt = profile.open;
    return {
      windows: windows.filter(([from]) => from < uncertainAt)
        .map(([from, to]) => [from, Math.min(to, uncertainAt)]),
      uncertainAt,
    };
  }
  return { windows };
}

function nextSession(profile, now, day) {
  const sessions = [];
  let uncertainBoundary;
  // A week plus the current local day covers the longest regular closure.
  for (let offset = 0; offset < 8; offset += 1) {
    const localDay = day + offset * DAY_MS;
    const { windows, uncertainAt } = dailyWindows(profile, localDay);
    for (const [from, to] of windows) {
      const start = sessionInstant(localDay, from);
      const end = sessionInstant(localDay, to);
      const previous = sessions.at(-1);
      if (previous?.end === start) previous.end = end;
      else sessions.push({ start, end });
    }
    if (uncertainAt !== undefined) {
      uncertainBoundary = sessionInstant(localDay, uncertainAt);
      break;
    }
    const last = sessions.at(-1);
    if (last?.end > now && last.end < sessionInstant(localDay, DAY_MINUTES)) break;
  }
  if (uncertainBoundary <= now) return { state: "unknown", reason: "holiday" };
  for (const { start, end } of sessions) {
    if (now < start) return { state: "closed", nextAt: start };
    if (now < end) {
      return end === uncertainBoundary
        ? { state: "open", reason: "holiday", validUntil: uncertainBoundary }
        : { state: "open", nextAt: end };
    }
  }
  return { state: "closed", reason: "holiday", validUntil: uncertainBoundary };
}

export function marketSession(instrument, now = Date.now()) {
  const profile = profileFor(instrument);
  if (!profile) return { state: "unknown", reason: "instrument" };
  if (profile.continuous) return { state: "open", continuous: true, source: profile.source };
  const instant = Number(now);
  const day = marketMidnight(instant);
  const session = nextSession(profile, instant, day);
  const date = new Date(day).toISOString().slice(0, 10);
  const holiday = profile.holidays[date];
  const specialHours = Boolean(holiday && Object.keys(holiday).length);
  const source = ((specialHours || session.reason === "holiday") && profile.holidaySource) || profile.source;
  const validUntil = Math.min(session.validUntil ?? Infinity, sessionInstant(day, DAY_MINUTES));
  return { ...session, specialHours, source, validUntil };
}

export function marketCountdown(nextAt, now) {
  const seconds = Math.max(0, Math.ceil((nextAt - now) / 1000));
  const days = Math.floor(seconds / 86_400);
  const hours = Math.floor(seconds / 3600) % 24;
  const minutes = Math.floor(seconds / 60) % 60;
  const parts = [hours, minutes, seconds % 60].map(value => String(value).padStart(2, "0"));
  return `${days ? `${days}d ` : ""}${parts.join(":")}`;
}
