// HTML → PDF with AppKit (used by tools/bompdf.py). osascript -l JavaScript html2pdf.js IN.html OUT.pdf [landscape]
ObjC.import('AppKit');
function run(argv) {
  var inPath = argv[0], outPath = argv[1], landscape = argv[2] === 'landscape';
  var data = $.NSData.dataWithContentsOfFile(inPath);
  var opts = $.NSDictionary.dictionaryWithObjectsForKeys(
    [$.NSHTMLTextDocumentType, $.NSNumber.numberWithInt(4)],
    [$.NSDocumentTypeDocumentAttribute, $.NSCharacterEncodingDocumentAttribute]);
  var astr = $.NSAttributedString.alloc.initWithDataOptionsDocumentAttributesError(data, opts, null, null);
  var info = $.NSPrintInfo.sharedPrintInfo.copy;
  info.paperSize = landscape ? $.NSMakeSize(1190.55, 841.89) : $.NSMakeSize(841.89, 1190.55);  // A3
  info.orientation = landscape ? 1 : 0;
  info.leftMargin = 28; info.rightMargin = 28; info.topMargin = 28; info.bottomMargin = 28;
  info.horizontalPagination = 1;  // fit width
  info.verticallyCentered = false;
  var w = info.paperSize.width - 56;
  var tv = $.NSTextView.alloc.initWithFrame($.NSMakeRect(0, 0, w, 100));
  tv.textStorage.setAttributedString(astr);
  tv.sizeToFit;
  var d = info.dictionary;
  d.setObjectForKey($.NSPrintSaveJob, $.NSPrintJobDisposition);
  d.setObjectForKey($.NSURL.fileURLWithPath(outPath), $.NSPrintJobSavingURL);
  var op = $.NSPrintOperation.printOperationWithViewPrintInfo(tv, info);
  op.showsPrintPanel = false; op.showsProgressPanel = false;
  op.runOperation;
  return 'ok';
}
