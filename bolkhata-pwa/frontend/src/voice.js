// Browser side of the voice loop: mic -> 1024-byte PCM16 frames -> /ws/voice, and streamed reply audio -> speaker.
export const ENGINES = ['live', 'rest', 'browser']
export const SPEECH_LANG = { hi: 'hi-IN', en: 'en-IN', kn: 'kn-IN', te: 'te-IN', ta: 'ta-IN' }
const SILENCE = new ArrayBuffer(1024)
const sleep = (ms) => new Promise((r) => setTimeout(r, ms))

export class VoiceClient {
  constructor(onEvent, { engine, lang, bargeIn }) {
    Object.assign(this, { onEvent, engine, lang, bargeIn })
    this.replyLang = lang === 'auto' ? 'en' : lang
    this.micOn = false
    this.speaking = false
    this.sources = []
    this.t0 = null
    this.seq = 0
    this.latestReq = null // only the reply to this request is shown
  }

  // ---------- socket
  connect() {
    this.ensureCtx()
    const proto = location.protocol === 'https:' ? 'wss' : 'ws'
    const ws = new WebSocket(`${proto}://${location.host}/ws/voice`)
    ws.binaryType = 'arraybuffer'
    ws.onopen = () => {
      this.onEvent({ type: 'connected' })
      this.sendJson({ type: 'start', engine: this.engine, lang: this.lang, bargeIn: this.bargeIn })
      if (this.queued) { // a command typed while reconnecting is sent now, not lost
        const q = this.queued
        this.queued = null
        this.sendJson(q)
      }
    }
    ws.onmessage = (e) => (typeof e.data === 'string' ? this.onJson(JSON.parse(e.data)) : this.onAudio(e.data))
    ws.onclose = () => {
      if (this.ws !== ws) return
      if (this.micOn) this.stopMicHardware() // never stay "listening" on a dead connection
      this.stopPlayback()
      this.onEvent({ type: 'disconnected' })
      setTimeout(() => this.ws === ws && this.connect(), 1500)
    }
    this.ws = ws
  }

  sendJson(obj) {
    if (this.ws?.readyState === 1) this.ws.send(JSON.stringify(obj))
  }

  setConfig(cfg) {
    Object.assign(this, cfg)
    this.sendJson({ type: 'config', ...cfg })
  }

  newReq() {
    this.latestReq = `c${++this.seq}`
    return this.latestReq
  }

  sendText(text) {
    this.t0 = performance.now()
    const msg = { type: 'text', text, id: this.newReq() }
    if (this.ws?.readyState === 1) this.sendJson(msg)
    else this.queued = msg // reconnecting: send it as soon as the socket is back (only the newest one)
  }

  tap(action, extra = {}) {
    this.t0 = performance.now()
    this.sendJson({ type: 'tap', action, ...extra, id: this.newReq() })
  }

  onJson(m) {
    switch (m.type) {
      case 'transcript':
        this.t0 = performance.now()
        if (m.req?.startsWith('v')) this.latestReq = m.req // a spoken sentence starts a new request
        break
      case 'reply':
      case 'ignored':
      case 'error':
        if (m.req && m.req !== this.latestReq) return // reply to an older request: never show it
        if (m.type === 'reply') this.replyLang = m.lang
        break
      case 'speech_start':
        if (this.bargeIn) this.stopPlayback()
        break
      case 'tts_start':
        this.rate = m.rate
        this.nextTime = 0
        this.firstAudio = false
        this.ttsDone = false
        this.left = null
        this.setSpeaking(true)
        break
      case 'tts_end':
        this.ttsDone = true
        if (m.interrupted) this.stopPlayback()
        if (!this.sources.length) this.setSpeaking(false)
        break
      case 'tts_failed':
        this.speakLocal(m.text, m.lang)
        break
      case 'engine_failed': {
        const next = ENGINES[ENGINES.indexOf(m.engine) + 1]
        if (next && next !== this.engine) {
          const wasOn = this.micOn
          this.stopMicHardware()
          this.setConfig({ engine: next })
          if (wasOn) this.micStart()
          m = { ...m, next }
        }
        break
      }
    }
    this.onEvent(m)
  }

  // ---------- playback (starts on the first chunk)
  ensureCtx() {
    if (!this.ctx) {
      this.ctx = new (window.AudioContext || window.webkitAudioContext)()
      this.outAn = this.ctx.createAnalyser() // the reply's voice, for the rings
      this.outAn.fftSize = 128
      this.outAn.smoothingTimeConstant = 0.75
      this.outAn.connect(this.ctx.destination)
    }
    if (this.ctx.state === 'suspended') this.ctx.resume()
    return this.ctx
  }

  /** Frequency magnitudes (0–255) of whoever is talking: the shopkeeper while listening, the reply while speaking. */
  levels() {
    const an = this.speaking ? this.outAn : this.micOn ? this.inAn : null
    if (!an) return null
    const bins = new Uint8Array(an.frequencyBinCount)
    an.getByteFrequencyData(bins)
    return bins
  }

  onAudio(buf) {
    let bytes = new Uint8Array(buf)
    if (this.left) {
      const b = new Uint8Array(bytes.length + 1)
      b[0] = this.left
      b.set(bytes, 1)
      bytes = b
      this.left = null
    }
    if (bytes.length % 2) {
      this.left = bytes[bytes.length - 1]
      bytes = bytes.slice(0, -1)
    }
    if (!bytes.length) return
    const pcm = new Int16Array(bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.length))
    const ctx = this.ctx
    const ab = ctx.createBuffer(1, pcm.length, this.rate || 22050)
    const ch = ab.getChannelData(0)
    for (let i = 0; i < pcm.length; i++) ch[i] = pcm[i] / 32768
    const src = ctx.createBufferSource()
    src.buffer = ab
    src.connect(this.outAn)
    const at = Math.max(this.nextTime, ctx.currentTime + 0.03)
    src.start(at)
    this.nextTime = at + ab.duration
    this.sources.push(src)
    src.onended = () => {
      this.sources = this.sources.filter((s) => s !== src)
      if (!this.sources.length && this.ttsDone) this.setSpeaking(false)
    }
    if (!this.firstAudio) {
      this.firstAudio = true
      this.reportReply(performance.now() + (at - ctx.currentTime) * 1000)
    }
  }

  reportReply(playAt) {
    if (this.t0 != null) this.onEvent({ type: 'latency', reply: Math.round(playAt - this.t0) })
    this.t0 = null
  }

  stopPlayback() {
    this.sources.forEach((s) => { try { s.stop() } catch { /* already stopped */ } })
    this.sources = []
    window.speechSynthesis?.cancel()
    this.setSpeaking(false)
  }

  speakLocal(text, lang) {
    if (!window.speechSynthesis) { this.onEvent({ type: 'playbackFailed' }); return }
    const u = new SpeechSynthesisUtterance(text)
    u.lang = SPEECH_LANG[lang] || 'en-IN'
    u.onstart = () => { this.setSpeaking(true); this.reportReply(performance.now()) }
    u.onend = () => this.setSpeaking(false)
    u.onerror = (e) => { this.setSpeaking(false); if (e.error !== 'interrupted' && e.error !== 'canceled') this.onEvent({ type: 'playbackFailed' }) }
    speechSynthesis.cancel()
    speechSynthesis.speak(u)
  }

  setSpeaking(v) {
    if (this.speaking === v) return
    this.speaking = v
    this.onEvent({ type: 'speaking', value: v })
  }

  // ---------- mic
  async micStart() {
    this.ensureCtx()
    if (this.engine === 'browser') return this.startRecognition()
    try {
      this.stream = await navigator.mediaDevices.getUserMedia({
        audio: { echoCancellation: true, noiseSuppression: true, autoGainControl: true, voiceIsolation: true, channelCount: 1 },
      })
    } catch (e) {
      this.onEvent({ type: 'nomic', reason: e?.name === 'NotFoundError' || e?.name === 'OverconstrainedError' ? 'missing' : 'denied' })
      return false
    }
    const applied = this.stream.getAudioTracks()[0]?.getSettings?.() || {}
    this.onEvent({ type: 'micSettings', settings: {
      noiseSuppression: applied.noiseSuppression, echoCancellation: applied.echoCancellation,
      autoGainControl: applied.autoGainControl, voiceIsolation: applied.voiceIsolation } })
    if (!this.workletLoaded) {
      await this.ctx.audioWorklet.addModule('/pcm-worklet.js')
      this.workletLoaded = true
    }
    this.src = this.ctx.createMediaStreamSource(this.stream)
    this.inAn = this.ctx.createAnalyser() // same stream as the one sent to Gnani, only read for the rings
    this.inAn.fftSize = 128
    this.inAn.smoothingTimeConstant = 0.7
    this.src.connect(this.inAn)
    this.node = new AudioWorkletNode(this.ctx, 'pcm16k')
    const mute = this.ctx.createGain()
    mute.gain.value = 0
    this.src.connect(this.node).connect(mute).connect(this.ctx.destination)
    // While the app talks, send silence so it doesn't hear itself, unless barge-in is on.
    this.node.port.onmessage = (e) => {
      if (this.ws?.readyState === 1) this.ws.send(this.speaking && !this.bargeIn ? SILENCE : e.data)
    }
    this.sendJson({ type: 'mic_on' })
    this.micOn = true
    return true
  }

  stopMicHardware() {
    this.micOn = false
    this.rec?.stop()
    this.rec = null
    this.node?.disconnect()
    this.src?.disconnect()
    this.inAn = null
    this.stream?.getTracks().forEach((t) => t.stop())
    this.node = this.src = this.stream = null
  }

  async micStop() {
    const engine = this.engine
    this.stopMicHardware()
    if (engine === 'browser') return
    for (let i = 0; i < 31; i++) { // ~1 s of silence at real-time pace, then commit
      if (this.ws?.readyState === 1) this.ws.send(SILENCE)
      await sleep(32)
    }
    this.sendJson({ type: 'commit' })
    if (engine === 'live') this.sendJson({ type: 'mic_off' })
  }

  startRecognition() {
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition
    if (!SR) {
      this.onEvent({ type: 'nomic', reason: 'missing' })
      return false
    }
    const r = new SR()
    r.lang = SPEECH_LANG[this.lang === 'auto' ? this.replyLang : this.lang]
    r.continuous = true
    r.interimResults = false
    r.onresult = (e) => {
      const res = e.results[e.results.length - 1]
      if (res.isFinal && !this.speaking) {
        this.sendText(res[0].transcript) // the server echoes it back as a transcript
      }
    }
    r.onerror = (e) => {
      if (e.error === 'not-allowed' || e.error === 'service-not-allowed') this.onEvent({ type: 'nomic', reason: 'denied' })
      if (e.error === 'audio-capture') this.onEvent({ type: 'nomic', reason: 'missing' })
    }
    r.onend = () => { if (this.rec === r) try { r.start() } catch { /* restarting too fast */ } }
    r.start()
    this.rec = r
    this.micOn = true
    return true
  }

  close() {
    this.stopMicHardware()
    this.stopPlayback()
    const ws = this.ws
    this.ws = null
    ws?.close()
  }
}
