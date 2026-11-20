const HISTORY_LIMIT = 120;

export function createProgressChannels({ maxIdleChannels = 128 } = {}) {
  const channels = new Map();
  const cancelled = new Set();
  let closed = false;

  function get(id) {
    let channel = channels.get(id);
    if (!channel) {
      channel = { events: [], clients: new Set(), observed: false };
      channels.set(id, channel);
    }
    return channel;
  }

  function releaseIfObserved(id, channel) {
    if (channel.clients.size || channels.get(id) !== channel) return;
    if (!channel.events.length || (channel.observed && isTerminal(channel))) channels.delete(id);
  }

  function isTerminal(channel) {
    return ["failed", "finished"].includes(channel.events.at(-1)?.status);
  }

  function publish(id, event) {
    if (!id || closed) return;
    const channel = get(id);
    if (event.status === "started") {
      channel.cancelled = false;
      cancelled.delete(id);
    }
    channel.events.push(event);
    if (channel.events.length > HISTORY_LIMIT) channel.events.shift();
    const message = `data: ${JSON.stringify(event)}\n\n`;
    for (const client of channel.clients) {
      try { client.write(message); }
      catch { channel.clients.delete(client); }
    }
    if (isTerminal(channel)) {
      releaseIfObserved(id, channel);
      if (channels.size > maxIdleChannels) {
        const idle = [...channels].filter(([, value]) => !value.clients.size && isTerminal(value));
        for (const [expired] of idle.slice(0, Math.max(0, idle.length - maxIdleChannels))) channels.delete(expired);
      }
    }
  }

  function attach(id, client) {
    if (shouldStopReconnect(id)) { client.end(); return () => {}; }
    const channel = get(id);
    channel.clients.add(client);
    channel.observed = true;
    for (const event of channel.events) {
      try { client.write(`data: ${JSON.stringify(event)}\n\n`); }
      catch { channel.clients.delete(client); break; }
    }
    if (channel.cancelled) {
      rememberCancellation(id);
      endClients(channel);
      releaseIfObserved(id, channel);
    }
    return () => {
      channel.clients.delete(client);
      releaseIfObserved(id, channel);
    };
  }

  function endClients(channel) {
    for (const client of channel.clients) {
      try { client.end(); } catch { /* A disconnected response cannot block cleanup. */ }
    }
    channel.clients.clear();
  }

  function rememberCancellation(id) {
    cancelled.delete(id);
    cancelled.add(id);
    if (cancelled.size > maxIdleChannels) cancelled.delete(cancelled.values().next().value);
  }

  function shouldStopReconnect(id) {
    return closed || (cancelled.has(id) && !channels.has(id));
  }

  function cancel(id, event) {
    if (!id || closed) return;
    const channel = get(id);
    channel.cancelled = true;
    rememberCancellation(id);
    publish(id, event);
    endClients(channel);
    releaseIfObserved(id, channel);
  }

  function close() {
    if (closed) return;
    closed = true;
    for (const channel of channels.values()) endClients(channel);
    channels.clear();
    cancelled.clear();
  }

  function stats() {
    let clients = 0;
    for (const channel of channels.values()) clients += channel.clients.size;
    return { channels: channels.size, clients };
  }

  return { publish, attach, cancel, shouldStopReconnect, close, stats };
}
