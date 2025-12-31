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

function isWordChar(char: string) {
  return /[a-zA-Z0-9]/.test(char);
}

function snapToWordBoundaries(
  text: string,
  start: number,
  end: number
) {
  let s = start;
  let e = end;

  while (s > 0 && isWordChar(text[s - 1])) {
    s--;
  }

  while (e < text.length && isWordChar(text[e])) {
    e++;
  }

  return { start: s, end: e };
}

export function getHighlightedSnippet(
  text: string,
  highlightIndex?: string,
  context = 40
): HighlightSnippet {
  if (!highlightIndex) {
    return text.length > 160 ? text.slice(0, 160) + "…" : text;
  }

  const [rawStart, rawEnd] = highlightIndex.split(":").map(Number);

  if (isNaN(rawStart) || isNaN(rawEnd)) {
    return text.length > 160 ? text.slice(0, 160) + "…" : text;
  }

  const { start, end } = snapToWordBoundaries(text, rawStart, rawEnd);

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

  const [rawStart, rawEnd] = highlightIndex.split(":").map(Number);

  if (isNaN(rawStart) || isNaN(rawEnd)) return null;

  const { start, end } = snapToWordBoundaries(text, rawStart, rawEnd);

  return {
    before: text.slice(0, start),
    highlight: text.slice(start, end),
    after: text.slice(end),
  };
}
