import { createContext, useContext, useCallback } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import type { Page } from '../types'
import { VALID_PAGES } from '../types'

interface NavigationContextValue {
  currentPage: Page
  navigate: (page: Page | string) => void
}

const NavigationContext = createContext<NavigationContextValue>({
  currentPage: 'dashboard',
  navigate: () => {},
})

export function NavigationProvider({ children }: { children: React.ReactNode }) {
  const navigate = useNavigate()
  const location = useLocation()

  const currentPage: Page = (() => {
    const path = location.pathname.replace(/^\//, '') || 'dashboard'
    return VALID_PAGES.includes(path as Page) ? (path as Page) : 'dashboard'
  })()

  const handleNavigate = useCallback(
    (page: Page | string) => {
      navigate(`/${page}`)
    },
    [navigate],
  )

  return (
    <NavigationContext.Provider value={{ currentPage, navigate: handleNavigate }}>
      {children}
    </NavigationContext.Provider>
  )
}

export function useNavigation() {
  return useContext(NavigationContext)
}
