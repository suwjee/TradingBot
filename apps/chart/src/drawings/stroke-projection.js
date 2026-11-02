// Pure presentation-side projection for brush/path strokes.
// Preserve Array#map(...).filter(...) semantics, including sparse point arrays,
// projection order and the optional path preview appended at the end.
export function collectProjectedStrokePoints(drawing, project, valid) {
  const output = [];
  const source = drawing.points || [];
  for (let index = 0; index < source.length; index++) {
    if (!(index in source)) continue;
    const point = project(source[index], index, source);
    if (valid(point)) output.push(point);
  }
  if (drawing.type === "path" && drawing.preview) {
    const preview = project(drawing.preview);
    if (valid(preview)) output.push(preview);
  }
  return output;
}
