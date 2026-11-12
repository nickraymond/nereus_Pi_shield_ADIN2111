// Join PDF files page by page with PDFKit (used by tools/boardpdf.sh).
// osascript -l JavaScript pdfmerge.js OUT.pdf IN1.pdf [IN2.pdf ...]
ObjC.import('PDFKit');
function run(argv) {
  var out = $.PDFDocument.alloc.init, n = 0;
  for (var k = 1; k < argv.length; k++) {
    var doc = $.PDFDocument.alloc.initWithURL($.NSURL.fileURLWithPath(argv[k]));
    if (doc.isNil() || doc.pageCount < 1) throw new Error('pdfmerge: cannot read ' + argv[k]);
    for (var i = 0; i < doc.pageCount; i++) out.insertPageAtIndex(doc.pageAtIndex(i), n++);
  }
  if (!out.writeToFile(argv[0])) throw new Error('pdfmerge: cannot write ' + argv[0]);
  return n + ' pages';
}
