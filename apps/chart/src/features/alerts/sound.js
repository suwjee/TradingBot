export function createAlertSound(window, onChange) {
  let context;
  let buffer;
  let playing;

  function stop() {
    playing?.source.stop();
    playing = null;
    onChange();
  }

  async function prepare() {
    if (!context) {
      const Audio = window.AudioContext || window.webkitAudioContext;
      if (!Audio) return false;
      context = new Audio();
    }
    if (context.state !== "running") await context.resume();
    return context.state === "running";
  }

  function play(seconds) {
    if (context?.state !== "running") return false;
    const now = context.currentTime;
    const end = now + seconds;
    if (playing && playing.end > now) {
      if (end > playing.end) {
        playing.source.stop(end);
        playing.end = end;
      }
      return true;
    }
    if (!buffer) {
      buffer = context.createBuffer(1, Math.round(context.sampleRate * 0.75), context.sampleRate);
      const samples = buffer.getChannelData(0);
      for (let index = 0; index < samples.length; index += 1) {
        const time = index / buffer.sampleRate;
        const secondNote = time >= 0.18;
        const phase = secondNote ? time - 0.18 : time;
        const envelope = Math.max(0, Math.min(1, phase / 0.015, (0.14 - phase) / 0.04));
        samples[index] = 0.16 * envelope * Math.sin(2 * Math.PI * phase * (secondNote ? 880 : 660));
      }
    }
    const source = context.createBufferSource();
    source.buffer = buffer;
    source.loop = true;
    source.connect(context.destination);
    source.onended = () => {
      source.disconnect();
      if (playing?.source !== source) return;
      playing = null;
      onChange();
    };
    source.start(now);
    source.stop(end);
    playing = { source, end };
    onChange();
    return true;
  }

  return { prepare, play, stop, isPlaying: () => Boolean(playing) };
}
