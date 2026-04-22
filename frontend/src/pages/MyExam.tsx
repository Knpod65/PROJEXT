import { useCallback, useEffect, useState } from "react";

import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import { Icon } from "@/components/ui/Icon";
import { Modal } from "@/components/ui/Modal";
import { Skeleton } from "@/components/ui/Skeleton";
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
  if (!sub || !sub.exists) return <span className="sub-badge sub-badge--draft">Not started</span>;
  const s = sub.status ?? "draft";
  const map: Record<string, string> = {
    draft: "In progress",
    submitted: "Submitted",
    approved: "Approved",
    rejected: "Returned",
    released: "Released",
  };
  return <span className={`sub-badge sub-badge--${s}`}>{map[s] ?? s}</span>;
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
  const step = submissionStep(sub);
  const isDone = sub?.status === "submitted" || sub?.status === "approved" || sub?.status === "released";

  return (
    <article className="teacher-section-card">
      <div className="teacher-section-card__main">
        <div>
          <strong className="teacher-section-card__course">
            {section.course?.course_id ?? "—"} {section.course?.course_name_th ?? ""}
          </strong>
          <span className="teacher-section-card__meta">
            Section {section.section_no} · {section.num_students} students
          </span>
          {section.schedules && section.schedules.length > 0 && (
            <span className="teacher-section-card__date">
              <Icon name="event" /> {section.schedules[0].exam_date} {section.schedules[0].exam_time}
              {section.schedules[0].room && ` · ${section.schedules[0].room.room_name}`}
            </span>
          )}
        </div>
        <div className="teacher-section-card__right">
          <StatusBadge sub={sub} />
          {!isDone && (
            <Button type="button" size="sm" onClick={onOpen}>
              {step === 0 ? "Start submission" : "Continue"}
            </Button>
          )}
          {isDone && sub?.status === "rejected" && (
            <Button type="button" size="sm" variant="danger" onClick={onOpen}>
              Revise
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
              title={["Confirm date", "Exam method", "Upload PDF", "Print spec"][n - 1]}
            />
          ))}
          <span className="submission-progress__label">Step {step} of 4</span>
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
      toast(err instanceof Error ? err.message : "Action failed.", "error");
    } finally {
      setBusy(false);
    }
  };

  const doStep1 = () =>
    run(async () => {
      await step1ConfirmDate(section.id);
      await onRefresh();
      toast("Date confirmed.", "success");
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
      toast("Exam method saved.", "success");
      setActiveStep(examType === "onsite" ? 3 : 4);
    });

  const doStep3 = () =>
    run(async () => {
      if (!pdfFile) { toast("Please select a PDF file.", "error"); return; }
      await step3UploadPdf(section.id, pdfFile, noCoverPage, isShared);
      await onRefresh();
      toast("PDF uploaded.", "success");
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
      toast("Print spec saved.", "success");
    });

  const doSubmit = () =>
    run(async () => {
      await submitForReview(section.id);
      await onRefresh();
      toast("Submitted for review.", "success");
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
      title={`${section.course?.course_id ?? ""} §${section.section_no} — Submission`}
      onClose={onClose}
      footer={
        <div className="inline-actions">
          <Button type="button" variant="outline" onClick={onClose}>Close</Button>
          {!alreadyDone && (
            <>
              {activeStep === 1 && (
                <Button type="button" loading={busy} onClick={doStep1}>
                  Confirm date
                </Button>
              )}
              {activeStep === 2 && (
                <Button type="button" loading={busy} onClick={doStep2}>
                  Save & continue
                </Button>
              )}
              {activeStep === 3 && (
                <Button type="button" loading={busy} disabled={!pdfFile} onClick={doStep3}>
                  Upload PDF
                </Button>
              )}
              {activeStep === 4 && (
                <>
                  <Button type="button" variant="outline" loading={busy} onClick={doStep4}>
                    Save print spec
                  </Button>
                  <Button type="button" loading={busy} onClick={doSubmit}>
                    Submit for review
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
              {["Date", "Method", "PDF", "Print"][n - 1]}
            </button>
          ))}
        </div>

        {/* Step 1: Confirm date */}
        {activeStep === 1 && (
          <div className="wizard-step-body">
            <h4>Step 1 — Confirm exam date</h4>
            {schedDate ? (
              <div className="wizard-info-box">
                <Icon name="event" />
                <div>
                  <strong>{schedDate} {schedTime ?? ""}</strong>
                  <span className="text-muted">Scheduled exam date for this section</span>
                </div>
              </div>
            ) : (
              <p className="text-muted">No exam date scheduled yet. You can still confirm when it is set.</p>
            )}
            {sub?.date_confirmed && <p className="wizard-done-note"><Icon name="check_circle" /> Date already confirmed.</p>}
          </div>
        )}

        {/* Step 2: Exam method */}
        {activeStep === 2 && (
          <div className="wizard-step-body">
            <h4>Step 2 — Exam method</h4>
            <div className="form-field">
              <label>Exam method</label>
              <select value={examType} onChange={(e) => setExamType(e.target.value as ExamTypeChoice)}>
                <option value="no_exam">No exam</option>
                <option value="online">Online</option>
                <option value="onsite">Onsite (written exam, requires PDF)</option>
                <option value="outside_sched">Outside scheduled time</option>
                <option value="in_class">In-class assessment</option>
              </select>
            </div>
            {examType === "onsite" && (
              <>
                <div className="form-field">
                  <label>Answer format(s)</label>
                  <div className="checkbox-group">
                    {(["on_paper", "mcq_omr", "a4_sheets", "booklet"] as AnswerFormat[]).map((fmt) => {
                      const labels: Record<string, string> = {
                        on_paper: "Write on exam paper",
                        mcq_omr: "OMR / optical sheet",
                        a4_sheets: "Separate A4 sheets",
                        booklet: "Answer booklet",
                      };
                      return (
                        <label key={fmt} className="checkbox-label">
                          <input
                            type="checkbox"
                            checked={answerFormats.includes(fmt)}
                            onChange={() => toggleAnswerFormat(fmt)}
                          />
                          {labels[fmt] ?? fmt}
                        </label>
                      );
                    })}
                  </div>
                </div>
                <div className="form-field">
                  <label htmlFor="a4-pages">A4 pages per copy</label>
                  <input
                    id="a4-pages"
                    type="number"
                    min={1}
                    max={100}
                    value={a4Pages}
                    onChange={(e) => setA4Pages(Number(e.target.value))}
                  />
                  <span className="form-hint">Number of pages in the exam paper</span>
                </div>
              </>
            )}
          </div>
        )}

        {/* Step 3: PDF upload (onsite only) */}
        {activeStep === 3 && (
          <div className="wizard-step-body">
            <h4>Step 3 — Upload exam PDF</h4>
            {!needsFile ? (
              <p className="text-muted">PDF upload is only required for onsite exams. Skip to Step 4.</p>
            ) : (
              <>
                <div className="form-field">
                  <label htmlFor="pdf-file">Exam PDF file</label>
                  <input
                    id="pdf-file"
                    type="file"
                    accept=".pdf"
                    onChange={(e) => setPdfFile(e.target.files?.[0] ?? null)}
                  />
                  <span className="form-hint">Max 20MB. Metadata will be stripped automatically.</span>
                </div>
                <div className="form-field form-field--checkbox">
                  <label className="checkbox-label">
                    <input
                      type="checkbox"
                      checked={noCoverPage}
                      onChange={(e) => setNoCoverPage(e.target.checked)}
                    />
                    I confirm this PDF has no cover page
                  </label>
                </div>
                <div className="form-field form-field--checkbox">
                  <label className="checkbox-label">
                    <input
                      type="checkbox"
                      checked={isShared}
                      onChange={(e) => setIsShared(e.target.checked)}
                    />
                    This is a shared exam (used by multiple sections)
                  </label>
                </div>
                {sub?.has_uploaded_pdf && (
                  <p className="wizard-done-note"><Icon name="check_circle" /> PDF already uploaded. Upload a new file to replace it.</p>
                )}
              </>
            )}
          </div>
        )}

        {/* Step 4: Print spec */}
        {activeStep === 4 && (
          <div className="wizard-step-body">
            <h4>Step 4 — Print specification</h4>
            {!needsFile ? (
              <p className="text-muted">Print spec is only required for onsite exams. You can submit directly.</p>
            ) : (
              <>
                <div className="form-field form-field--checkbox">
                  <label className="checkbox-label">
                    <input
                      type="checkbox"
                      checked={duplex}
                      onChange={(e) => setDuplex(e.target.checked)}
                    />
                    Double-sided printing (duplex)
                  </label>
                </div>
                <div className="form-field">
                  <label>Stapling</label>
                  <select value={staple} onChange={(e) => setStaple(e.target.value as PrintStaple)}>
                    <option value="none">No staple</option>
                    <option value="corner_left">Corner staple (top-left)</option>
                    <option value="side_left">Side staple (left edge)</option>
                    <option value="custom">Custom — split by page range</option>
                  </select>
                </div>
                {staple === "custom" && (
                  <div className="form-field">
                    <label htmlFor="staple-page">Staple at page</label>
                    <input
                      id="staple-page"
                      type="number"
                      min={1}
                      placeholder="e.g. 4"
                      value={staplePage}
                      onChange={(e) => setStaplePage(e.target.value === "" ? "" : Number(e.target.value))}
                    />
                    <span className="form-hint">Staple separates set at this page number</span>
                  </div>
                )}
                <div className="form-field">
                  <label htmlFor="print-note">Note to print shop (optional)</label>
                  <textarea
                    id="print-note"
                    rows={2}
                    value={printNote}
                    placeholder="e.g. Keep 5 spare copies"
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
              <strong>{sub?.status === "approved" ? "Approved" : sub?.status === "released" ? "Released to print shop" : "Submitted — awaiting review"}</strong>
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
      toast(err instanceof Error ? err.message : "Failed to load sections.", "error");
    } finally {
      setLoading(false);
    }
  }, [activePeriod, toast]);

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
      <section className="page-hero">
        <div>
          <span className="page-hero__eyebrow">Teacher workspace</span>
          <h1 className="page-hero__title">My exam submissions</h1>
          <p className="page-hero__description">
            Complete exam submission for each of your assigned courses. All sections must be submitted before the deadline.
          </p>
        </div>
        <div className="page-hero__actions">
          <Button type="button" variant="outline" onClick={() => void loadSections()} disabled={loading}>
            Refresh
          </Button>
        </div>
      </section>

      <div className="stitch-metric-grid">
        <article className="dashboard-metric dashboard-metric--accent">
          <div className="dashboard-metric__icon"><Icon name="menu_book" /></div>
          <div className="dashboard-metric__body">
            <p className="dashboard-metric__label">Assigned courses</p>
            <strong className="dashboard-metric__value">{sections.length}</strong>
          </div>
        </article>
        <article className="dashboard-metric dashboard-metric--success">
          <div className="dashboard-metric__icon"><Icon name="task_alt" /></div>
          <div className="dashboard-metric__body">
            <p className="dashboard-metric__label">Submitted</p>
            <strong className="dashboard-metric__value">{submitted}</strong>
          </div>
        </article>
        <article className="dashboard-metric dashboard-metric--warning">
          <div className="dashboard-metric__icon"><Icon name="pending_actions" /></div>
          <div className="dashboard-metric__body">
            <p className="dashboard-metric__label">Pending</p>
            <strong className="dashboard-metric__value">{pending}</strong>
          </div>
        </article>
      </div>

      {loading ? (
        <div className="page-stack">
          {[0, 1, 2].map((i) => <Skeleton key={i} className="dashboard-skeleton" />)}
        </div>
      ) : sections.length === 0 ? (
        <EmptyState
          icon={<Icon name="menu_book" />}
          title="No courses assigned"
          description="You have no sections assigned for this term. Contact your department administrator."
        />
      ) : (
        <Card title="Your courses" subtitle={`${activePeriod?.label ?? "Current term"}`}>
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
