import { cx } from "@/utils/cx";

interface SkeletonProps {
  className?: string;
}

export function Skeleton({ className }: SkeletonProps) {
  return <div className={cx("ui-skeleton", className)} aria-hidden="true" />;
}
