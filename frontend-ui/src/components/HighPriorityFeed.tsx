import { useState } from "react";
import type { HighPriorityReviewItem } from "../services/api";
import { getHighlightedSnippet, getFullHighlightParts } from "../utils/highlight";

type Props = {
  items: HighPriorityReviewItem[];
};

function formatLabel(label: string) {
  return label.replaceAll("_", " ");
}

function HighPriorityItem({ item }: { item: HighPriorityReviewItem }) {
  const [expanded, setExpanded] = useState(false);

  const snippet = getHighlightedSnippet(
    item.review,
    item.highlightIndex
  );

  const canExpand = typeof snippet !== "string" && (snippet.truncatedStart || snippet.truncatedEnd);

  const full = expanded
    ? getFullHighlightParts(item.review, item.highlightIndex)
    : null;
  

  return (
    <div
      className="
        rounded-xl border border-slate-200 bg-white p-4 shadow-sm
        dark:border-slate-700 dark:bg-slate-900
      "
    >
      <div className="mb-2 text-[11px] text-slate-500 dark:text-slate-400">
        <span>[{item.date}]</span>

        <span className="ml-2 font-medium text-red-600 dark:text-red-400">
          {formatLabel(item.label)}
        </span>

        {item.flightNumber && (
          <span className="ml-1">
            on flight{" "}
            <span className="font-medium text-slate-700 dark:text-slate-200">
              {item.flightNumber}
            </span>
          </span>
        )}
      </div>

      <div className="text-sm leading-relaxed text-slate-800 dark:text-slate-100">
        {!expanded ? (
          typeof snippet === "string" ? (
            snippet
          ) : (
            <>
              {snippet.truncatedStart && "…"}
              {snippet.before}
              <mark className="rounded bg-red-100/80 px-1 text-slate-800 dark:text-slate-100 dark:bg-red-500/25">
                {snippet.highlight}
              </mark>
              {snippet.after}
              {snippet.truncatedEnd && "…"}
            </>
          )
        ) : full ? (
          <>
            {full.before}
            <mark className="rounded bg-red-100/80 px-1 text-slate-800 dark:text-slate-100 dark:bg-red-500/25">
              {full.highlight}
            </mark>
            {full.after}
          </>
        ) : (
          item.review
        )}
      </div>
      
      {canExpand && (
        <button
          onClick={() => setExpanded((v) => !v)}
          className="
            mt-2 text-xs font-medium text-red-600
            hover:underline dark:text-red-400
          "
        >
          {expanded ? (
            <>
              <span>▲</span> <span>Show less</span>
            </>
          ) : (
            <>
              <span>▼</span> <span>Show more</span>
            </>
          )}
        </button>
      )}
    </div>
  );
}

export default function HighPriorityFeed({ items }: Props) {
  if (!items.length) {
    return (
      <p className="text-sm text-gray-500">
        No high priority issues found.
      </p>
    );
  }
  return (
    <div className="space-y-4">
      {items.map((item, idx) => (
        <HighPriorityItem key={idx} item={item} />
      ))}
    </div>
  );
}
    
