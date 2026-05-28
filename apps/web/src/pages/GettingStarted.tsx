import { useTranslation } from 'react-i18next'

type Page = 'status' | 'weekly' | 'dialogue' | 'reality' | 'history' | 'rubric' | 'checkpoint' | 'provider' | 'getting-started'

export default function GettingStarted({ onNavigate }: { onNavigate: (page: Page) => void }) {
  const { t } = useTranslation()
  const section = 'mb-6 p-4 border border-gray-700 rounded-lg'

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold">{t('gettingStarted.title')}</h2>

      <div className={section}>
        <h3 className="text-sm font-medium mb-2">{t('gettingStarted.providerDisabled')}</h3>
        <p className="text-gray-400 text-sm leading-relaxed">{t('gettingStarted.providerDisabledDesc')}</p>
        <button className="mt-2 px-3 py-1.5 text-xs bg-gray-800 text-white rounded hover:bg-gray-700" onClick={() => onNavigate('provider')}>
          {t('gettingStarted.openProviderSettings')}
        </button>
      </div>

      <div className={section}>
        <h3 className="text-sm font-medium mb-2">{t('gettingStarted.firstWeeklyReview')}</h3>
        <p className="text-gray-400 text-sm leading-relaxed">{t('gettingStarted.firstWeeklyReviewDesc')}</p>
        <button className="mt-2 px-3 py-1.5 text-xs bg-gray-800 text-white rounded hover:bg-gray-700" onClick={() => onNavigate('weekly')}>
          {t('gettingStarted.startWeeklyReview')}
        </button>
      </div>

      <div className={section}>
        <h3 className="text-sm font-medium mb-2">{t('gettingStarted.checkHealth')}</h3>
        <p className="text-gray-400 text-sm leading-relaxed">{t('gettingStarted.checkHealthDesc')}</p>
      </div>

      <div className={section}>
        <h3 className="text-sm font-medium mb-2">{t('gettingStarted.backup')}</h3>
        <p className="text-gray-400 text-sm leading-relaxed">{t('gettingStarted.backupDesc')}</p>
      </div>

      <div className="mb-6 p-4 border border-gray-600 rounded-lg">
        <h3 className="text-sm font-medium mb-2">{t('gettingStarted.boundaries')}</h3>
        <p className="text-gray-400 text-sm leading-relaxed">
          <strong>{t('gettingStarted.p6')}</strong> {t('gettingStarted.p6Desc')}<br />
          <strong>{t('gettingStarted.p7')}</strong> {t('gettingStarted.p7Desc')}<br />
          <strong>{t('gettingStarted.p8')}</strong> {t('gettingStarted.p8Desc')}<br />
          <strong>{t('gettingStarted.providerOutput')}</strong> {t('gettingStarted.providerOutputDesc')}
        </p>
      </div>
    </div>
  )
}
