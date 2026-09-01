const paths = {
  cursor:'M5 3l14 9-6 2-3 6L5 3z', trend:'M4 17L18 5M14 5h4v4', arrow:'M4 18L19 5m-6 0h6v6', ray:'M4 17L16 5M13 5h3v3', channel:'M4 16L15 5M9 20L20 9M4 12h4m8 0h4', path:'M4 18l5-9 5 6 6-10', hline:'M3 12h18', vline:'M12 3v18', brush:'M4 17c4-6 7 3 12-7 2-4 4-5 4-5', rect:'M4 5h16v14H4z', circle:'M12 4a8 8 0 1 0 0 16 8 8 0 0 0 0-16z', text:'M5 5h14M12 5v14', fib:'M4 5h16M4 9h16M4 14h16M4 19h16', measure:'M4 17L17 4l3 3L7 20zM10 11l3 3m0-6 3 3', zoom:'M10 4a6 6 0 1 0 0 12 6 6 0 0 0 0-12zm5 11 5 5M10 7v6m-3-3h6', magnet:'M7 4v8a5 5 0 0 0 10 0V4M7 8h4M13 8h4', eye:'M2 12s4-6 10-6 10 6 10 6-4 6-10 6S2 12 2 12zm10-3a3 3 0 1 0 0 6 3 3 0 0 0 0-6z', erase:'M5 16l8-10 6 5-6 8H8z', trash:'M5 7h14M9 7V4h6v3m-8 0 1 13h8l1-13', undo:'M9 7L4 12l5 5M5 12h8a6 6 0 0 1 6 6', redo:'M15 7l5 5-5 5m4-5h-8a6 6 0 0 0-6 6', search:'M11 5a6 6 0 1 0 0 12 6 6 0 0 0 0-12zm5 11 4 4', calendar:'M5 7h14v12H5zM8 3v4m8-4v4M5 10h14', camera:'M4 8h4l2-3h4l2 3h4v11H4zM12 11a3 3 0 1 0 0 6 3 3 0 0 0 0-6z', settings:'M12 8a4 4 0 1 0 0 8 4 4 0 0 0 0-8zm0-5v2m0 14v2M3 12h2m14 0h2M5 5l2 2m10 10 2 2m0-14-2 2M7 17l-2 2', chevron:'M8 10l4 4 4-4', layers:'M4 8l8-4 8 4-8 4-8-4zm0 5 8 4 8-4', fullscreen:'M5 9V5h4m6 0h4v4M5 15v4h4m6 0h4v-4', plus:'M12 5v14M5 12h14', info:'M12 11v6m0-10v.01', close:'M6 6l12 12M18 6 6 18', lock:'M7 10h10v10H7zM9 10V7a3 3 0 0 1 6 0v3', unlock:'M7 10h10v10H7zM9 10V7a3 3 0 0 1 5-2', copy:'M8 8h11v11H8zM5 16H4V5h11v1', more:'M5 12h.01M12 12h.01M19 12h.01'
};
paths.refresh = 'M20 11a8 8 0 1 0-2.34 5.66M20 4v7h-7';
paths.line = 'M4 19L20 5';
paths.chartSettings = 'M4 7h10m4 0h2M4 17h2m4 0h10M14 4v6M6 14v6';
paths.dashboard = 'M4 4h6v6H4zM14 4h6v6h-6zM4 14h6v6H4zM14 14h6v6h-6z';
paths.chart = 'M4 18V8m5 10V4m5 14v-7m5 7V6';
paths.bell = 'M6 17h12l-1.5-2.4V10a4.5 4.5 0 0 0-9 0v4.6L6 17zm4 3h4';
paths.history = 'M4 12a8 8 0 1 0 2.3-5.7L4 8.5M4 4v4.5h4.5M12 8v4l3 2';
paths.profile = 'M12 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8zm-7 8a7 7 0 0 1 14 0';
paths.pin = 'M8 4h8l-1 6 3 3v1H6v-1l3-3-1-6zm4 10v6';
paths.folder = 'M3 6h7l2 2h9v10H3zM3 6v12';
paths.target = 'M12 3v4m0 10v4M3 12h4m10 0h4M12 8a4 4 0 1 0 0 8 4 4 0 0 0 0-8z';
paths.database = 'M4 6c0-2 3.6-3 8-3s8 1 8 3-3.6 3-8 3-8-1-8-3zm0 0v6c0 2 3.6 3 8 3s8-1 8-3V6M4 12v6c0 2 3.6 3 8 3s8-1 8-3v-6';
paths.shield = 'M12 3l7 3v5c0 4.6-2.8 7.8-7 10-4.2-2.2-7-5.4-7-10V6l7-3zm-3 9 2 2 4-5';
paths.candles = 'M6 4v16m-2-5h4v-6H4v6zm8-12v18m-2-7h4V7h-4v6zm8-7v14m-2-3h4V9h-4v8z';
paths.activity = 'M3 12h4l2-6 4 12 2-6h6';
paths.login = 'M10 5H5v14h5m4-4 4-3-4-3m4 3H9';
paths.restart = 'M19 8a7 7 0 1 0 1 7M19 4v4h-4';
paths.play = 'M8 5l11 7-11 7V5z';
paths.download = 'M12 4v11m-4-4 4 4 4-4M5 20h14';
paths.exportCandles = 'M6 3h8l4 4v14H6zM14 3v5h4M9 17v-5m3 5V9m3 8v-3';
paths.logout = 'M14 5h5v14h-5m-4-4 4-3-4-3m4 3H5';
paths.server = 'M5 5h14v5H5zm0 9h14v5H5zm3-6h.01M8 17h.01';
paths.language = 'M4 5h10M9 3c2 2.2 3 4.7 3 7s-1 4.8-3 7m-2 1 2 2 2-2M14 19h6m-3-2c-1.7-2.5-2.6-5.3-2.6-8S15.3 3.5 17 1m-3 18h6';
// Deliberately reads as a familiar WWW globe at toolbar sizes, matching the
// browser action rather than the generic language selector glyph.
paths.web = 'M3 12a9 9 0 1 0 18 0A9 9 0 0 0 3 12zm1.2 0h15.6M12 3c2.2 2.4 3.3 5.4 3.3 9S14.2 18.6 12 21M12 3C9.8 5.4 8.7 8.4 8.7 12s1.1 6.6 3.3 9M6 7.1h12M6 16.9h12M5.6 9.1l1.1 4 1.2-4 1.2 4 1.1-4M11.1 9.1l1.1 4 1.2-4 1.2 4 1.1-4';
paths.check = 'm5 12 4 4L19 6';
paths.cross = 'M6 6l12 12M18 6 6 18';
export function icon(name, size=20){return `<svg width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="${paths[name] || paths.info}"/></svg>`}
