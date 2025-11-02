/**
 * Reusable pagination component using Blueprint.js.
 */

import { Button } from "@blueprintjs/core";
import { paginationContainer } from "../../styles/common";
import { spacing } from "../../styles/theme";

interface PaginationProps {
  currentPage: number;
  totalPages: number;
  onPrevious: () => void;
  onNext: () => void;
  hasPrevious: boolean;
  hasNext: boolean;
}

export default function Pagination({
  currentPage,
  totalPages,
  onPrevious,
  onNext,
  hasPrevious,
  hasNext,
}: PaginationProps) {
  return (
    <div style={paginationContainer}>
      <Button
        icon="chevron-left"
        text="Previous"
        onClick={onPrevious}
        disabled={!hasPrevious}
        intent="none"
      />
      <span style={{ margin: `0 ${spacing.md}` }}>
        Page {currentPage} of {totalPages}
      </span>
      <Button
        icon="chevron-right"
        text="Next"
        onClick={onNext}
        disabled={!hasNext}
        intent="none"
      />
    </div>
  );
}

