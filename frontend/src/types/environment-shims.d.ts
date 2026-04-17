/*
 * TEMPORARY FALLBACK ONLY
 *
 * Purpose:
 * - This file exists only for environments where `node_modules` are unavailable
 *   and TypeScript cannot resolve real React/router type packages.
 *
 * Required removal/disable condition:
 * - As soon as real npm dependencies are installed (especially `react`, `react-dom`,
 *   `react-router-dom`, `@types/react`, and `@types/react-dom`), this shim MUST be
 *   removed or excluded from compilation.
 * - Recommended: add `src/types/environment-shims.d.ts` to `exclude` in `tsconfig.json`
 *   after dependency installation, then run type-check/build with real types.
 *
 * Conflict prevention note:
 * - This shim is intentionally broad and should never coexist with real type packages
 *   in normal development. Keep it disabled when real `@types/*` are present.
 *
 * Policy for this repository:
 * - Do NOT add new shim files in later milestones unless explicitly approved.
 */

declare module "react" {
  export type ReactNode = any;
  export type DependencyList = ReadonlyArray<unknown>;
  export interface CSSProperties {
    [key: string]: string | number | undefined;
  }

  export interface HTMLAttributes<T = any> {
    children?: ReactNode;
    [key: string]: any;
  }

  export interface ButtonHTMLAttributes<T = any> extends HTMLAttributes<T> {}

  export interface FormEvent<T = any> {
    preventDefault: () => void;
    target: T;
    currentTarget: T;
  }

  export const Fragment: any;

  export function createContext<T = any>(defaultValue: T): any;
  export function useContext<T = any>(context: any): T;
  export function useMemo<T>(factory: () => T, deps?: DependencyList): T;
  export function useState<S>(initialState: S | (() => S)): [S, (value: S | ((prevState: S) => S)) => void];
  export function useEffect(effect: (...args: any[]) => any, deps?: DependencyList): void;
  export function useCallback<T extends (...args: any[]) => any>(callback: T, deps?: DependencyList): T;
}

declare module "react/jsx-runtime" {
  export const Fragment: any;
  export function jsx(type: any, props: any, key?: any): any;
  export function jsxs(type: any, props: any, key?: any): any;
}

declare module "react-dom" {
  export function createPortal(children: any, container: Element | DocumentFragment): any;
}

declare module "react-dom/client" {
  const ReactDOM: {
    createRoot: (container: Element | DocumentFragment | null) => {
      render: (children: any) => void;
      unmount?: () => void;
    };
  };

  export default ReactDOM;
}

declare module "react-router-dom" {
  export const BrowserRouter: any;
  export const NavLink: any;
  export const Navigate: any;
  export const Outlet: any;
  export const Route: any;
  export const Routes: any;
  export function useLocation(): any;
  export function useNavigate(): (...args: any[]) => any;
}

declare module "vite/client" {}

declare namespace JSX {
  interface Element {}

  interface IntrinsicElements {
    [elementName: string]: any;
  }
}
