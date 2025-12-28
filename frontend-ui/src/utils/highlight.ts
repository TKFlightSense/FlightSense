export type HighlightSnippet =
  | string
  | {
      before: string;
      highlight: string;
      after: string;
      truncatedStart: boolean;
      truncatedEnd: boolean;
    };

export type FullHighlightParts = {
  before: string;
  highlight: string;
  after: string;
};

export function getHighlightedSnippet(
  text: string,
  highlightIndex?: string,
  context = 40
): HighlightSnippet {
  if (!highlightIndex) {
    return text.length > 160 ? text.slice(0, 160) + "…" : text;
  }

  const [start, end] = highlightIndex.split(":").map(Number);

  if (isNaN(start) || isNaN(end)) {
    return text.length > 160 ? text.slice(0, 160) + "…" : text;
  }

  const snippetStart = Math.max(0, start - context);
  const snippetEnd = Math.min(text.length, end + context);

  return {
    before: text.slice(snippetStart, start),
    highlight: text.slice(start, end),
    after: text.slice(end, snippetEnd),
    truncatedStart: snippetStart > 0,
    truncatedEnd: snippetEnd < text.length,
  };
}


export function getFullHighlightParts(
  text: string,
  highlightIndex?: string
): FullHighlightParts | null {
  if (!highlightIndex) return null;

  const [start, end] = highlightIndex.split(":").map(Number);

  if (isNaN(start) || isNaN(end)) return null;

  return {
    before: text.slice(0, start),
    highlight: text.slice(start, end),
    after: text.slice(end),
  };
}
