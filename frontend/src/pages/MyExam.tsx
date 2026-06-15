import { useCallback, useEffect, useState } from "react";

import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import { Icon } from "@/components/ui/Icon";
import { Modal } from "@/components/ui/Modal";
import { PageHeader } from "@/components/ui/PageHeader";
import { PageSkeleton } from "@/components/ui/PageSkeleton";
import { StatusChip, type StatusTone } from "@/components/ui/StatusChip";
import { useI18n } from "@/i18n";
import {
  getSubmissionForSection,
  step1ConfirmDate,
  step2ExamType,
  step3UploadPdf,
  step4PrintSpec,
  submitForReview,
  type AnswerFormat,
  type ExamTypeChoice,
  type PrintStaple,
} from "@/services/submission.service";
import { listSections } from "@/services/sections.service";
import { usePeriod } from "@/store/period.store";
import { useUi } from "@/store/ui.store";
import type { SectionOut, SubmissionDetail } from "@/types/api";

// ── Status helpers ─────────────────────────────────────────────

function submissionStep(sub: SubmissionDetail | null): number {
  if (!sub || !sub.exists) return 0;
  if (sub.status === "submitted" || sub.status === "approved" || sub.status === "released") return 5;
  if (sub.exam_type_choice === "onsite") {
    if (sub.has_uploaded_pdf && sub.exam_type_choice) return 4;
    if (sub.has_uploaded_pdf) return 3;
    if (sub.exam_type_choice) return 3;
  }
  if (sub.exam_type_choice) return 2;
  if (sub.date_confirmed) return 1;
  return 0;
}

function StatusBadge({ sub }: { sub: SubmissionDetail | null }) {
  const { t } = useI18n();
  if (!sub || !sub.exists) return <StatusChip tone="draft">{t("myExam.status.notStarted")}</StatusChip>;
  const s = sub.status ?? "draft";
  const tones: Record<string, StatusTone> = {
    draft: "draft",
    submitted: "information",
    approved: "success",
    rejected: "danger",
    released: "success",
  };
  return <StatusChip tone={tones[s] ?? "neutral"}>{t(`myExam.status.${s}`)}</StatusChip>;
}

// ── Section card ────────────────────────────────────────────────

function SectionCard({
  section,
  sub,
  onOpen,
}: {
  section: SectionOut;
  sub: SubmissionDetail | null;
  onOpen: () => void;
}) {
  const { t } = useI18n();
  const step = submissionStep(sub);
  const isDone = sub?.status === "submitted" || sub?.status === "approved" || sub?.status === "released";

  return (
    <article className="teacher-section-card">
      <div className="teacher-section-card__main">
        <div>
          <strong className="teacher-section-card__course">
            {section.course?.course_id ?? "-"} {section.course?.course_name_th ?? ""}
          </strong>
          <span className="teacher-section-card__meta">
            {t("myExam.sectionMeta", { section: section.section_no, students: section.num_students })}
          </span>
          {section.schedules && section.schedules.length > 0 && (
            <>
              <span className="teacher-section-card__date">
                <Icon name="event" /> {section.schedules[0].exam_date} {section.schedules[0].exam_time}
                {` | ${t("myExam.examRoom", { room: section.schedules[0].room?.room_name ?? t("myExam.notAssigned") })}`}
              </span>
              <span className="teacher-section-card__meta">
                {t("myExam.teachingRoom", { room: section.teaching_room?.room_name ?? t("myExam.notRecorded") })}
              </span>
            </>
          )}
        </div>
        <div className="teacher-section-card__right">
          <StatusBadge sub={sub} />
          {!isDone && (
            <Button type="button" size="sm" onClick={onOpen}>
              {step === 0 ? t("myExam.actions.start") : t("myExam.actions.continue")}
            </Button>
          )}
          {isDone && sub?.status === "rejected" && (
            <Button type="button" size="sm" variant="danger" onClick={onOpen}>
              {t("myExam.actions.revise")}
            </Button>
          )}
        </div>
      </div>
      {sub?.rejected_reason && (
        <div className="teacher-section-card__rejection">
          <Icon name="info" /> <span>{sub.rejected_reason}</span>
        </div>
      )}
      {step > 0 && step < 5 && (
        <div className="submission-progress">
          {[1, 2, 3, 4].map((n) => (
            <div
              key={n}
              className={`submission-progress__dot${n <= step ? " done" : ""}`}
              title={t(`myExam.steps.${n}.short`)}
            />
          ))}
          <span className="submission-progress__label">{t("myExam.progress", { step })}</span>
        </div>
      )}
    </article>
  );
}

// ── Wizard modal ────────────────────────────────────────────────

type WizardStep = 1 | 2 | 3 | 4;

function SubmissionWizard({
  section,
  sub,
  onClose,
  onRefresh,
}: {
  section: SectionOut;
  sub: SubmissionDetail | null;
  onClose: () => void;
  onRefresh: () => Promise<void>;
}) {
  const { t } = useI18n();
  const { toast } = useUi();
  const [busy, setBusy] = useState(false);
  const [activeStep, setActiveStep] = useState<WizardStep>(() => {
    const s = submissionStep(sub);
    if (s >= 4) return 4;
    if (s === 3) return 4;
    if (s === 2) return (sub?.exam_type_choice as string) === "onsite" ? 3 : 4;
    if (s === 1) return 2;
    return 1;
  });

  // Step 2 state
  const [examType, setExamType] = useState<ExamTypeChoice>(
    (sub?.exam_type_choice as ExamTypeChoice) ?? "online",
  );
  const [answerFormats, setAnswerFormats] = useState<AnswerFormat[]>(
    (sub?.answer_formats as AnswerFormat[]) ?? [],
  );
  const [a4Pages, setA4Pages] = useState(sub?.a4_pages_count ?? 0);

  // Step 3 state
  const [pdfFile, setPdfFile] = useState<File | null>(null);
  const [noCoverPage, setNoCoverPage] = useState(sub?.no_cover_page_confirmed ?? false);
  const [isShared, setIsShared] = useState(sub?.is_shared_exam ?? false);

  // Step 4 state
  const [duplex, setDuplex] = useState(false);
  const [staple, setStaple] = useState<PrintStaple>("none");
  const [staplePage, setStaplePage] = useState<number | "">("");
  const [printNote, setPrintNote] = useState("");

  const schedDate = section.schedules?.[0]?.exam_date ?? null;
  const schedTime = section.schedules?.[0]?.exam_time ?? null;
  const needsFile = examType === "onsite";

  const run = async (fn: () => Promise<void>) => {
    setBusy(true);
    try {
      await fn();
    } catch (err) {
      toast(err instanceof Error ? err.message : t("myExam.toast.actionFailed"), "error");
    } finally {
      setBusy(false);
    }
  };

  const doStep1 = () =>
    run(async () => {
      await step1ConfirmDate(section.id);
      await onRefresh();
      toast(t("myExam.toast.dateConfirmed"), "success");
      setActiveStep(2);
    });

  const doStep2 = () =>
    run(async () => {
      const fmts = examType === "onsite" ? answerFormats : [];
      await step2ExamType({
        section_id: section.id,
        exam_type_choice: examType,
        answer_formats: fmts,
        a4_pages_count: a4Pages,
      });
      await onRefresh();
      toast(t("myExam.toast.methodSaved"), "success");
      setActiveStep(examType === "onsite" ? 3 : 4);
    });

  const doStep3 = () =>
    run(async () => {
      if (!pdfFile) { toast(t("myExam.toast.selectPdf"), "error"); return; }
      await step3UploadPdf(section.id, pdfFile, noCoverPage, isShared);
      await onRefresh();
      toast(t("myExam.toast.pdfUploaded"), "success");
      setActiveStep(4);
    });

  const doStep4 = () =>
    run(async () => {
      await step4PrintSpec({
        section_id: section.id,
        print_duplex: duplex,
        print_staple: staple,
        print_staple_page: staplePage !== "" ? Number(staplePage) : null,
        print_note: printNote || null,
      });
      await onRefresh();
      toast(t("myExam.toast.printSaved"), "success");
    });

  const doSubmit = () =>
    run(async () => {
      await submitForReview(section.id);
      await onRefresh();
      toast(t("myExam.toast.submitted"), "success");
      onClose();
    });

  const toggleAnswerFormat = (fmt: AnswerFormat) =>
    setAnswerFormats((prev) =>
      prev.includes(fmt) ? prev.filter((f) => f !== fmt) : [...prev, fmt],
    );

  const alreadyDone = sub?.status === "submitted" || sub?.status === "approved" || sub?.status === "released";

  const stepDone = (n: WizardStep) => {
    const s = submissionStep(sub);
    return s >= n;
  };

  return (
    <Modal
      open
      title={t("myExam.modalTitle", { course: section.course?.course_id ?? "", section: section.section_no })}
      onClose={onClose}
      footer={
        <div className="inline-actions">
          <Button type="button" variant="outline" onClick={onClose}>{t("common.close")}</Button>
          {!alreadyDone && (
            <>
              {activeStep === 1 && (
                <Button type="button" loading={busy} onClick={doStep1}>
                  {t("myExam.actions.confirmDate")}
                </Button>
              )}
              {activeStep === 2 && (
                <Button type="button" loading={busy} onClick={doStep2}>
                  {t("myExam.actions.saveContinue")}
                </Button>
              )}
              {activeStep === 3 && (
                <Button type="button" loading={busy} disabled={!pdfFile} onClick={doStep3}>
                  {t("myExam.actions.uploadPdf")}
                </Button>
              )}
              {activeStep === 4 && (
                <>
                  <Button type="button" variant="outline" loading={busy} onClick={doStep4}>
                    {t("myExam.actions.savePrint")}
                  </Button>
                  <Button type="button" loading={busy} onClick={doSubmit}>
                    {t("myExam.actions.submitReview")}
                  </Button>
                </>
              )}
            </>
          )}
        </div>
      }
    >
      <div className="wizard-body">
        {/* Step tabs */}
        <div className="wizard-steps">
          {([1, 2, 3, 4] as WizardStep[]).map((n) => (
            <button
              key={n}
              type="button"
              className={`wizard-step${activeStep === n ? " active" : ""}${stepDone(n) ? " done" : ""}`}
              onClick={() => !alreadyDone && setActiveStep(n)}
            >
              {stepDone(n) ? <Icon name="check_circle" /> : <span>{n}</span>}
              {t(`myExam.steps.${n}.short`)}
            </button>
          ))}
        </div>

        {/* Step 1: Confirm date */}
        {activeStep === 1 && (
          <div className="wizard-step-body">
            <h4>{t("myExam.steps.1.title")}</h4>
            {schedDate ? (
              <div className="wizard-info-box">
                <Icon name="event" />
                <div>
                  <strong>{schedDate} {schedTime ?? ""}</strong>
                  <span className="text-muted">{t("myExam.steps.1.scheduledDate")}</span>
                </div>
              </div>
            ) : (
              <p className="text-muted">{t("myExam.steps.1.noDate")}</p>
            )}
            {sub?.date_confirmed && <p className="wizard-done-note"><Icon name="check_circle" /> {t("myExam.steps.1.confirmed")}</p>}
          </div>
        )}

        {/* Step 2: Exam method */}
        {activeStep === 2 && (
          <div className="wizard-step-body">
            <h4>{t("myExam.steps.2.title")}</h4>
            <div className="form-field">
              <label>{t("myExam.method.label")}</label>
              <select value={examType} onChange={(e) => setExamType(e.target.value as ExamTypeChoice)}>
                <option value="no_exam">{t("myExam.method.noExam")}</option>
                <option value="online">{t("myExam.method.online")}</option>
                <option value="onsite">{t("myExam.method.onsite")}</option>
                <option value="outside_sched">{t("myExam.method.outside")}</option>
                <option value="in_class">{t("myExam.method.inClass")}</option>
              </select>
            </div>
            {examType === "onsite" && (
              <>
                <div className="form-field">
                  <label>{t("myExam.answerFormat.label")}</label>
                  <div className="checkbox-group">
                    {(["on_paper", "mcq_omr", "a4_sheets", "booklet"] as AnswerFormat[]).map((fmt) => {
                      return (
                        <label key={fmt} className="checkbox-label">
                          <input
                            type="checkbox"
                            checked={answerFormats.includes(fmt)}
                            onChange={() => toggleAnswerFormat(fmt)}
                          />
                          {t(`myExam.answerFormat.${fmt}`)}
                        </label>
                      );
                    })}
                  </div>
                </div>
                <div className="form-field">
                  <label htmlFor="a4-pages">{t("myExam.a4Pages")}</label>
                  <input
                    id="a4-pages"
                    type="number"
                    min={1}
                    max={100}
                    value={a4Pages}
                    onChange={(e) => setA4Pages(Number(e.target.value))}
                  />
                  <span className="form-hint">{t("myExam.a4PagesHint")}</span>
                </div>
              </>
            )}
          </div>
        )}

        {/* Step 3: PDF upload (onsite only) */}
        {activeStep === 3 && (
          <div className="wizard-step-body">
            <h4>{t("myExam.steps.3.title")}</h4>
            {!needsFile ? (
              <p className="text-muted">{t("myExam.steps.3.notRequired")}</p>
            ) : (
              <>
                <div className="form-field">
                  <label htmlFor="pdf-file">{t("myExam.pdf.label")}</label>
                  <input
                    id="pdf-file"
                    type="file"
                    accept=".pdf"
                    onChange={(e) => setPdfFile(e.target.files?.[0] ?? null)}
                  />
                  <span className="form-hint">{t("myExam.pdf.hint")}</span>
                </div>
                <div className="form-field form-field--checkbox">
                  <label className="checkbox-label">
                    <input
                      type="checkbox"
                      checked={noCoverPage}
                      onChange={(e) => setNoCoverPage(e.target.checked)}
                    />
                    {t("myExam.pdf.noCover")}
                  </label>
                </div>
                <div className="form-field form-field--checkbox">
                  <label className="checkbox-label">
                    <input
                      type="checkbox"
                      checked={isShared}
                      onChange={(e) => setIsShared(e.target.checked)}
                    />
                    {t("myExam.pdf.shared")}
                  </label>
                </div>
                {sub?.has_uploaded_pdf && (
                  <p className="wizard-done-note"><Icon name="check_circle" /> {t("myExam.pdf.alreadyUploaded")}</p>
                )}
              </>
            )}
          </div>
        )}

        {/* Step 4: Print spec */}
        {activeStep === 4 && (
          <div className="wizard-step-body">
            <h4>{t("myExam.steps.4.title")}</h4>
            {!needsFile ? (
              <p className="text-muted">{t("myExam.print.notRequired")}</p>
            ) : (
              <>
                <div className="form-field form-field--checkbox">
                  <label className="checkbox-label">
                    <input
                      type="checkbox"
                      checked={duplex}
                      onChange={(e) => setDuplex(e.target.checked)}
                    />
                    {t("myExam.print.duplex")}
                  </label>
                </div>
                <div className="form-field">
                  <label>{t("myExam.print.stapling")}</label>
                  <select value={staple} onChange={(e) => setStaple(e.target.value as PrintStaple)}>
                    <option value="none">{t("myExam.print.staple.none")}</option>
                    <option value="corner_left">{t("myExam.print.staple.corner")}</option>
                    <option value="side_left">{t("myExam.print.staple.side")}</option>
                    <option value="custom">{t("myExam.print.staple.custom")}</option>
                  </select>
                </div>
                {staple === "custom" && (
                  <div className="form-field">
                    <label htmlFor="staple-page">{t("myExam.print.staplePage")}</label>
                    <input
                      id="staple-page"
                      type="number"
                      min={1}
                      placeholder={t("myExam.print.staplePagePlaceholder")}
                      value={staplePage}
                      onChange={(e) => setStaplePage(e.target.value === "" ? "" : Number(e.target.value))}
                    />
                    <span className="form-hint">{t("myExam.print.staplePageHint")}</span>
                  </div>
                )}
                <div className="form-field">
                  <label htmlFor="print-note">{t("myExam.print.note")}</label>
                  <textarea
                    id="print-note"
                    rows={2}
                    value={printNote}
                    placeholder={t("myExam.print.notePlaceholder")}
                    onChange={(e) => setPrintNote(e.target.value)}
                  />
                </div>
              </>
            )}
          </div>
        )}

        {alreadyDone && (
          <div className="wizard-done-banner">
            <Icon name={sub?.status === "approved" ? "verified" : "schedule"} />
            <div>
              <strong>{sub?.status === "approved" ? t("myExam.done.approved") : sub?.status === "released" ? t("myExam.done.released") : t("myExam.done.submitted")}</strong>
              {sub?.admin_note && <p className="text-muted">{sub.admin_note}</p>}
            </div>
          </div>
        )}
      </div>
    </Modal>
  );
}

// ── Main page ───────────────────────────────────────────────────

export function MyExamPage() {
  const { t } = useI18n();
  const { toast } = useUi();
  const { activePeriod } = usePeriod();

  const [sections, setSections] = useState<SectionOut[]>([]);
  const [loading, setLoading] = useState(true);
  const [subs, setSubs] = useState<Record<number, SubmissionDetail>>({});
  const [subsLoading, setSubsLoading] = useState(false);

  const [openSection, setOpenSection] = useState<SectionOut | null>(null);

  const loadSections = useCallback(async () => {
    setLoading(true);
    try {
      const data = await listSections({
        semester: activePeriod?.semester ?? "2",
        academic_year: activePeriod?.academic_year ?? "2568",
      });
      setSections(data);
    } catch (err) {
      toast(err instanceof Error ? err.message : t("myExam.toast.loadFailed"), "error");
    } finally {
      setLoading(false);
    }
  }, [activePeriod, t, toast]);

  const loadSubmissions = useCallback(
    async (sectionList: SectionOut[]) => {
      setSubsLoading(true);
      const results = await Promise.allSettled(
        sectionList.map((s) => getSubmissionForSection(s.id)),
      );
      const map: Record<number, SubmissionDetail> = {};
      results.forEach((r, i) => {
        if (r.status === "fulfilled") map[sectionList[i].id] = r.value;
      });
      setSubs(map);
      setSubsLoading(false);
    },
    [],
  );

  useEffect(() => {
    void loadSections();
  }, [loadSections]);

  useEffect(() => {
    if (sections.length > 0) void loadSubmissions(sections);
  }, [sections, loadSubmissions]);

  const refreshSub = useCallback(async () => {
    if (!openSection) return;
    const updated = await getSubmissionForSection(openSection.id);
    setSubs((prev) => ({ ...prev, [openSection.id]: updated }));
  }, [openSection]);

  const submitted = Object.values(subs).filter((s) => s.status === "submitted" || s.status === "approved" || s.status === "released").length;
  const pending = sections.length - submitted;

  return (
    <div className="page-stack page-stack--spacious">
      <PageHeader
        eyebrow={t("myExam.eyebrow")}
        title={t("myExam.title")}
        description={t("myExam.description")}
        actions={
          <Button type="button" variant="outline" onClick={() => void loadSections()} disabled={loading}>
            {t("common.refresh")}
          </Button>
        }
      />

      <div className="stitch-metric-grid">
        <article className="dashboard-metric dashboard-metric--accent">
          <div className="dashboard-metric__icon"><Icon name="menu_book" /></div>
          <div className="dashboard-metric__body">
            <p className="dashboard-metric__label">{t("myExam.metrics.assigned")}</p>
            <strong className="dashboard-metric__value">{sections.length}</strong>
          </div>
        </article>
        <article className="dashboard-metric dashboard-metric--success">
          <div className="dashboard-metric__icon"><Icon name="task_alt" /></div>
          <div className="dashboard-metric__body">
            <p className="dashboard-metric__label">{t("myExam.metrics.submitted")}</p>
            <strong className="dashboard-metric__value">{submitted}</strong>
          </div>
        </article>
        <article className="dashboard-metric dashboard-metric--warning">
          <div className="dashboard-metric__icon"><Icon name="pending_actions" /></div>
          <div className="dashboard-metric__body">
            <p className="dashboard-metric__label">{t("myExam.metrics.pending")}</p>
            <strong className="dashboard-metric__value">{pending}</strong>
          </div>
        </article>
      </div>

      {loading ? (
        <PageSkeleton cards={3} rows={3} />
      ) : sections.length === 0 ? (
        <EmptyState
          icon={<Icon name="menu_book" />}
          title={t("myExam.empty.title")}
          description={t("myExam.empty.description")}
        />
      ) : (
        <Card title={t("myExam.responsibilities")} subtitle={activePeriod?.label ?? t("myExam.currentTerm")}>
          <div className="page-stack">
            {sections.map((section) => (
              <SectionCard
                key={section.id}
                section={section}
                sub={subsLoading ? null : (subs[section.id] ?? null)}
                onOpen={() => setOpenSection(section)}
              />
            ))}
          </div>
        </Card>
      )}

      {openSection && (
        <SubmissionWizard
          section={openSection}
          sub={subs[openSection.id] ?? null}
          onClose={() => setOpenSection(null)}
          onRefresh={refreshSub}
        />
      )}
    </div>
  );
}
