import { gsap } from 'gsap'

const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches

export function fadeIn(el: HTMLElement, duration = 0.3) {
  if (prefersReduced) return
  gsap.fromTo(el, { opacity: 0, y: 8 }, { opacity: 1, y: 0, duration, ease: 'power2.out' })
}

export function expandIn(el: HTMLElement, duration = 0.25) {
  if (prefersReduced) return
  gsap.fromTo(el, { opacity: 0, height: 0 }, { opacity: 1, height: 'auto', duration, ease: 'power2.out' })
}

export function collapseOut(el: HTMLElement, duration = 0.2) {
  if (prefersReduced) return Promise.resolve()
  return gsap.to(el, { opacity: 0, height: 0, duration, ease: 'power2.in' })
}

export function pulseSuccess(el: HTMLElement) {
  if (prefersReduced) return
  gsap.fromTo(el, { scale: 1 }, { scale: 1.02, duration: 0.15, yoyo: true, repeat: 1, ease: 'power2.inOut' })
}

export function shakeError(el: HTMLElement) {
  if (prefersReduced) return
  gsap.fromTo(el, { x: 0 }, { x: 4, duration: 0.08, yoyo: true, repeat: 5, ease: 'power2.inOut' })
}
