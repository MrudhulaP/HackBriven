// Resamples the mic to 16 kHz mono PCM16 and posts frames of exactly 1024 bytes (512 samples).
class Pcm16k extends AudioWorkletProcessor {
  constructor() {
    super()
    this.ratio = sampleRate / 16000
    this.pos = 0
    this.prev = 0
    this.out = new Int16Array(512)
    this.n = 0
  }
  push(s) {
    s = Math.max(-1, Math.min(1, s))
    this.out[this.n++] = s < 0 ? s * 0x8000 : s * 0x7fff
    if (this.n === 512) {
      this.port.postMessage(this.out.buffer.slice(0))
      this.n = 0
    }
  }
  process(inputs) {
    const ch = inputs[0] && inputs[0][0]
    if (!ch) return true
    const get = (k) => (k < 0 ? this.prev : ch[k])
    while (this.pos <= ch.length - 1) {
      const i = Math.floor(this.pos), f = this.pos - i
      this.push(f === 0 ? get(i) : get(i) * (1 - f) + get(i + 1) * f)
      this.pos += this.ratio
    }
    this.pos -= ch.length
    this.prev = ch[ch.length - 1]
    return true
  }
}
registerProcessor('pcm16k', Pcm16k)
