import { useI18n } from "@/i18n";
import { cx } from "@/utils/cx";

import type { ImportWizardStepItem } from "@/hooks/useImportWizard";

interface ImportWizardStepsProps {
  steps: ImportWizardStepItem[];
  currentStep: number;
}

export function ImportWizardSteps({ currentStep, steps }: ImportWizardStepsProps) {
  const { t } = useI18n();

  return (
    <ol className="import-wizard-steps" aria-label={t("import.v2.reviewAria")}>
      {steps.map((step) => {
        const isActive = step.number === currentStep;
        const isCompleted = step.number < currentStep;

        return (
          <li key={step.key} className={cx("import-wizard-steps__item", isActive && "is-active", isCompleted && "is-complete")}>
            <span className="import-wizard-steps__badge">{step.number}</span>
            <div>
              <strong>{step.title}</strong>
            </div>
          </li>
        );
      })}
    </ol>
  );
}
