import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

import { en } from "./en";
import { th } from "./th";

export type AppLanguage = "th" | "en";
type TranslationDictionary = Record<string, string>;
type TranslationValue = string | number | boolean | null | undefined;
export type TranslationParams = Record<string, TranslationValue>;

interface I18nContextValue {
  language: AppLanguage;
  locale: string;
  setLanguage: (language: AppLanguage) => void;
  t: (key: string, params?: TranslationParams) => string;
}

const LANGUAGE_STORAGE_KEY = "ems.language";
const dictionaries: Record<AppLanguage, TranslationDictionary> = { en, th };
const missingKeys = new Set<string>();

const backendMessageMap: Record<string, string> = {
  "You are not assigned to this workspace. Please check your role and try again.": "errors.workspaceNotAssigned",
  "Invalid username or password.": "errors.invalidCredentials",
  "Student ID was not found in the current exam records.": "public.studentSearch.notFoundDescription",
};

function normalizeLanguage(value: string | null | undefined): AppLanguage | null {
  if (!value) {
    return null;
  }

  const normalized = value.trim().toLowerCase();
  if (normalized.startsWith("th")) {
    return "th";
  }
  if (normalized.startsWith("en")) {
    return "en";
  }

  return null;
}

function detectInitialLanguage(): AppLanguage {
  if (typeof window !== "undefined") {
    const storedLanguage = normalizeLanguage(window.localStorage.getItem(LANGUAGE_STORAGE_KEY));
    if (storedLanguage) {
      return storedLanguage;
    }
  }

  if (typeof navigator !== "undefined") {
    const browserLanguage = normalizeLanguage(navigator.language);
    if (browserLanguage) {
      return browserLanguage;
    }
  }

  return "en";
}

function interpolate(template: string, params?: TranslationParams) {
  if (!params) {
    return template;
  }

  return template.replace(/\{(\w+)\}/g, (_, key: string) => {
    const value = params[key];
    return value === null || value === undefined ? "" : String(value);
  });
}

function resolveTranslationTemplate(language: AppLanguage, key: string) {
  return dictionaries[language][key] ?? dictionaries.en[key] ?? null;
}

function logMissingKey(key: string) {
  if (missingKeys.has(key)) {
    return;
  }

  missingKeys.add(key);
  console.warn(`[EMS i18n] Missing translation key: ${key}`);
}

let currentLanguage = detectInitialLanguage();

function getLocaleForLanguage(language: AppLanguage) {
  return language === "th" ? "th-TH" : "en-US";
}

function syncDocumentLanguage(language: AppLanguage) {
  if (typeof document !== "undefined") {
    document.documentElement.lang = language;
  }
}

function persistLanguage(language: AppLanguage) {
  if (typeof window !== "undefined") {
    window.localStorage.setItem(LANGUAGE_STORAGE_KEY, language);
  }
}

export function getCurrentLanguage() {
  return currentLanguage;
}

export function getCurrentLocale() {
  return getLocaleForLanguage(currentLanguage);
}

export function translateForLanguage(language: AppLanguage, key: string, params?: TranslationParams) {
  const template = resolveTranslationTemplate(language, key);
  if (!template) {
    logMissingKey(key);
    return key;
  }

  return interpolate(template, params);
}

export function translate(key: string, params?: TranslationParams) {
  return translateForLanguage(currentLanguage, key, params);
}

export function translateWithFallback(key: string, fallback: string, params?: TranslationParams) {
  const template = resolveTranslationTemplate(currentLanguage, key);
  if (!template) {
    logMissingKey(key);
    return interpolate(fallback, params);
  }

  return interpolate(template, params);
}

export function translateApiMessage(message: string) {
  const normalizedMessage = message.trim();
  const mappedKey = backendMessageMap[normalizedMessage];
  return mappedKey ? translate(mappedKey) : message;
}

const I18nContext = createContext<I18nContextValue | undefined>(undefined);

export function I18nProvider({ children }: { children: ReactNode }) {
  const [language, setLanguageState] = useState<AppLanguage>(() => currentLanguage);

  currentLanguage = language;

  useEffect(() => {
    currentLanguage = language;
    persistLanguage(language);
    syncDocumentLanguage(language);
  }, [language]);

  const setLanguage = useCallback((nextLanguage: AppLanguage) => {
    setLanguageState(nextLanguage);
  }, []);

  const t = useCallback(
    (key: string, params?: TranslationParams) => translateForLanguage(language, key, params),
    [language],
  );

  const value = useMemo(
    () => ({
      language,
      locale: getLocaleForLanguage(language),
      setLanguage,
      t,
    }),
    [language, setLanguage, t],
  );

  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>;
}

export function useI18n() {
  const context = useContext(I18nContext);
  if (!context) {
    throw new Error("useI18n must be used inside I18nProvider");
  }

  return context;
}
