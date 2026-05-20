import React from "react";
import type { ReactNode } from "react";

export interface RenderTabButtonOptions {
  active: boolean;
  onClick: () => void;
  label: string;
}

export function renderTabButton({ active, onClick, label }: RenderTabButtonOptions): ReactNode {
  const cls = active
    ? "border-blue-500 text-blue-600"
    : "border-transparent text-gray-500 hover:text-gray-700";
  return (
    <button
      onClick={onClick}
      className={`px-4 py-2 text-sm font-medium border-b-2 ${cls}`}
    >
      {label}
    </button>
  );
}
