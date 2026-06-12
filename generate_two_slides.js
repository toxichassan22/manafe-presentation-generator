var PptxGenJS = require('pptxgenjs');
var fs = require('fs');
var path = require('path');

var pptx = new PptxGenJS();
pptx.layout = 'LAYOUT_WIDE';
pptx.author = 'منافع الاقتصادية';
pptx.title = 'عرض تجريبي';
pptx.lang = 'ar-SA';

var LOGO_PATH = path.join(__dirname, 'manafe-logo.png');
var logo = '';
try {
  logo = 'data:image/png;base64,' + fs.readFileSync(LOGO_PATH).toString('base64');
} catch(e) {}

var googleMapsLink = 'https://maps.app.goo.gl/P5AmubtJAsfnkptU6';

function addText(slide, text, x, y, w, h, opts = {}) {
  slide.addText(text, { x, y, w, h, fontFace: 'Arial', lang: 'ar-SA', rtl: true, fit: 'shrink', margin: 0.06, ...opts });
}

function addTitle(slide, title, subtitle) {
  addText(slide, title, 0.55, 0.35, 12.2, 0.55, { fontSize: 25, bold: true, color: '7A0C0C', align: 'right' });
  if (subtitle) {
    addText(slide, subtitle, 0.55, 0.88, 12.2, 0.35, { fontSize: 11, color: '777777', align: 'right' });
  }
  slide.addShape(pptx.ShapeType.line, { x: 0.55, y: 1.28, w: 12.2, h: 0, line: { color: '7A0C0C', width: 1.2 } });
}

function addFooter(slide, label, pageNum) {
  if (logo) {
    slide.addImage({ data: logo, x: 0.45, y: 6.63, w: 0.75, h: 0.45 });
  }
  addText(slide, 'عرض تجريبي للموقع', 1.25, 6.9, 4, 0.25, { fontSize: 8, color: '999999' });
  slide.addShape(pptx.ShapeType.roundRect, { x: 12.22, y: 6.88, w: 0.42, h: 0.26, rectRadius: 0.04, fill: { color: '7A0C0C' }, line: { color: '7A0C0C' } });
  addText(slide, String(pageNum), 12.22, 6.89, 0.42, 0.22, { fontSize: 9, color: 'FFFFFF', align: 'center' });
}

// Slide 1: Cover Slide
var s1 = pptx.addSlide();
s1.background = { color: 'FBFAF8' };
s1.addShape(pptx.ShapeType.rect, { x: 0, y: 0, w: 13.33, h: 1.1, fill: { color: '7A0C0C' }, line: { color: '7A0C0C' } });
addText(s1, 'عرض مشروع استثماري تجريبي', 0.65, 0.32, 12, 0.35, { fontSize: 18, bold: true, color: 'FFFFFF' });
if (logo) {
  s1.addImage({ data: logo, x: 0.65, y: 1.35, w: 1.6, h: 1.15 });
}
addText(s1, 'مشروع تجربة خريطة قوقل ماب', 1.3, 2.3, 10.8, 0.85, { fontSize: 34, bold: true, color: '7A0C0C', align: 'center' });
addText(s1, 'تطوير وتجربة الأزرار التفاعلية', 1.3, 3.2, 10.8, 0.35, { fontSize: 15, color: '777777', align: 'center' });
addFooter(s1, 'الغلاف', 1);

// Slide 2: Location Features Slide
var s2 = pptx.addSlide();
addTitle(s2, 'مميزات موقع المشروع', 'موقع استراتيجي متصل ومؤثر تجارياً');

var features = [
  'يقع المشروع على تقاطع طرق حيوية رئيسية تسهل الوصول.',
  'قريب من مراكز الخدمة والنمو السكاني الواعد.',
  'المنطقة المحيطة تتمتع بنشاط تجاري واقتصادي مستمر.'
];

// Add bullet points
addText(s2, features.map(f => '• ' + f).join('\n'), 0.95, 1.8, 11.5, 3.5, { fontSize: 16, color: '444444', valign: 'top' });

// Add Google Maps button
s2.addShape(pptx.ShapeType.roundRect, { x: 8.8, y: 5.4, w: 4.0, h: 0.5, rectRadius: 0.1, fill: { color: '7A0C0C' }, line: { color: '7A0C0C' } });
addText(s2, 'فتح موقع المشروع على Google Maps', 8.8, 5.48, 4.0, 0.35, {
  fontSize: 11,
  bold: true,
  color: 'FFFFFF',
  align: 'center',
  hyperlink: { url: googleMapsLink, tooltip: 'Google Maps' }
});

addFooter(s2, 'مميزات الموقع', 2);

// Output filename
var outName = 'demo_presentation_' + Date.now() + '.pptx';
var outPath = path.join(__dirname, 'outputs', outName);

if (!fs.existsSync(path.join(__dirname, 'outputs'))) {
  fs.mkdirSync(path.join(__dirname, 'outputs'), { recursive: true });
}

pptx.writeFile({ fileName: outPath }).then(function() {
  console.log('SUCCESS:' + outName);
}).catch(function(err) {
  console.error('ERROR:', err);
});
