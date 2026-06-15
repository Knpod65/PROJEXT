import { Skeleton } from "./Skeleton";

interface PageSkeletonProps {
  cards?: number;
  rows?: number;
}

export function PageSkeleton({ cards = 3, rows = 5 }: PageSkeletonProps) {
  return (
    <div className="page-stack page-stack--spacious page-skeleton" aria-busy="true">
      <Skeleton className="page-skeleton__hero" />
      <div className="page-skeleton__cards">
        {Array.from({ length: cards }).map((_, index) => <Skeleton className="page-skeleton__card" key={index} />)}
      </div>
      <div className="page-skeleton__rows">
        {Array.from({ length: rows }).map((_, index) => <Skeleton className="page-skeleton__row" key={index} />)}
      </div>
    </div>
  );
}
