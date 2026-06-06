import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'
import en from './locales/en.json'
import zh from './locales/zh.json'

export const STORAGE_KEY = 'alters_lab_language'
const saved = localStorage.getItem(STORAGE_KEY)
const lng = saved === 'zh' || saved === 'en' ? saved : 'en'

i18n.use(initReactI18next).init({
  resources: { en: { translation: en }, zh: { translation: zh } },
  lng,
  fallbackLng: 'en',
  interpolation: { escapeValue: false },
})

export default i18n
