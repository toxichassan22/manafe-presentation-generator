// ═══════════════════════════════════════════════════════════════
// GLM 5.1 + Gemini Flash — Full Pipeline v2
// ═══════════════════════════════════════════════════════════════

var PptxGenJS = require('pptxgenjs');
var fs = require('fs');
var path = require('path');
var { execSync } = require('child_process');

var ZAI_KEY = process.env.ZAI_KEY;
var OPENROUTER_KEY = process.env.OPENROUTER_KEY;
var ZAI_BASE = 'https://api.z.ai/api/paas/v4';
var OPENROUTER_BASE = 'https://openrouter.ai/api/v1';
var GLM_MODEL = 'glm-5.1';
var IMAGE_MODEL = 'google/gemini-3.1-flash-image-preview';
var OUTPUT_DIR = path.join(__dirname, 'outputs');
var LOGO_PATH = path.join(__dirname, 'manafe-logo.png');

if (!fs.existsSync(OUTPUT_DIR)) fs.mkdirSync(OUTPUT_DIR, { recursive: true });

var logoBase64 = '';
try {
  logoBase64 = 'data:image/png;base64,' + fs.readFileSync(LOGO_PATH).toString('base64');
} catch(e) {}

// ═══ System Prompt ═══
var SYSTEM_PROMPT = `You are a professional PowerPoint designer for "منافع الاقتصادية" (Manafe).

BRAND: Burgundy #8B1A1A, White #FFFFFF, Gold #C4A35A, Font: Cairo

You generate pptxgenjs Node.js scripts. You design the ENTIRE visual presentation.

API RULES:
- var PptxGenJS = require('pptxgenjs');
- Shapes: slide.addShape('rect', { x:0, y:0, w:'100%', h:1, fill:{color:'8B1A1A'} })
- Text: slide.addText('Hello', { x:1, y:1, w:5, h:1, fontSize:24, fontFace:'Cairo', color:'FFFFFF' })
- Image: slide.addImage({ data: logo, x:0.5, y:0.5, w:1, h:1 })
- Chart: slide.addChart(pptx.charts.BAR, [{name:'Sales',labels:['Q1','Q2','Q3'],values:[10,20,30]}], {x:1,y:2,w:5,h:3})
- Pie: slide.addChart(pptx.charts.PIE, [{name:'Dist',labels:['A','B','C'],values:[40,35,25]}], {x:1,y:2,w:4,h:3})
- Table: slide.addTable(rows, {x:1,y:2,w:10,border:{pt:1,color:'CCCCCC'}})
- Colors: hex WITHOUT '#'. NEVER put base64 in addText().
- Do NOT redeclare "logo". It is already provided.

OUTPUT: pptx.writeFile({ fileName: 'D:/workflow/outputs/presentation_TIMESTAMP.pptx' }).then(...)
Replace TIMESTAMP with Date.now().

=== IMAGE PLACEMENT (VERY IMPORTANT) ===
You MUST specify EXACTLY where images go using this format in your code:

// IMAGE_SPEC: slide=2, x=0.3, y=1.5, w=5, h=4, prompt="modern luxury apartment building with glass facade"
// IMAGE_SPEC: slide=5, x=7.5, y=1.5, w=5.5, h=4.5, prompt="interior of a luxury apartment living room"

Rules for IMAGE_SPEC:
- Only put images on CONTENT slides, NEVER on cover or thank you slides
- The x, y, w, h define where the image will be placed
- The prompt describes what the image should show
- Leave SPACE in your layout for the image (don't put text where image will be)
- Max 4 images total
- Each image must have a clear purpose related to the slide content

=== LINK PLACEMENT ===
If projectData contains a googleMapsLink, you MUST add a clickable hyperlink text on the 'مميزات الموقع' (Location Features) slide:
slide.addText('موقع المشروع على قوقل ماب (Google Maps)', { x: x, y: y, w: w, h: h, hyperlink: { url: googleMapsLink_value_from_projectData }, color: 'C4A35A', fontFace: 'Cairo', fontSize: 14, underline: true })

Make 12 slides. Use charts and tables for data. All text same language as topic.
Return ONLY JS code.`;

// ═══ Step 1: GLM generates presentation with image specs ═══
async function generateWithGLM(topic, projectData) {
  console.log('\n[1/3] GLM 5.1 generating presentation...');

  var userMessage = 'TOPIC: "' + topic + '"';
  if (projectData) {
    userMessage += '\n\nPROJECT DATA:\n' + JSON.stringify(projectData, null, 2);
  }

  var response = await fetch(ZAI_BASE + '/chat/completions', {
    method: 'POST',
    headers: { 'Authorization': 'Bearer ' + ZAI_KEY, 'Content-Type': 'application/json' },
    body: JSON.stringify({
      model: GLM_MODEL,
      messages: [
        { role: 'system', content: SYSTEM_PROMPT },
        { role: 'user', content: userMessage }
      ],
      temperature: 0.7,
      max_tokens: 14000
    })
  });

  var data = await response.json();
  if (!data.choices || !data.choices[0]) throw new Error('GLM failed: ' + JSON.stringify(data));

  if (data.usage) {
    var u = data.usage;
    console.log('  ✓ Tokens: ' + u.total_tokens + ' | Cost: $' + ((u.prompt_tokens * 0.98 + u.completion_tokens * 3.08) / 1000000).toFixed(4));
  }

  var code = data.choices[0].message.content.trim();
  code = code.replace(/^```javascript\s*/i, '').replace(/^```js\s*/i, '').replace(/^```\s*/i, '');
  code = code.replace(/\s*```\s*$/, '');

  // Extract IMAGE_SPEC comments
  var imageSpecs = [];
  var specRegex = /\/\/\s*IMAGE_SPEC:\s*slide=(\d+),\s*x=([\d.]+),\s*y=([\d.]+),\s*w=([\d.]+),\s*h=([\d.]+),\s*prompt="([^"]+)"/g;
  var match;
  while ((match = specRegex.exec(code)) !== null) {
    imageSpecs.push({
      slide: parseInt(match[1]),
      x: parseFloat(match[2]),
      y: parseFloat(match[3]),
      w: parseFloat(match[4]),
      h: parseFloat(match[5]),
      prompt: match[6]
    });
  }

  // Remove IMAGE_SPEC comments from code
  code = code.replace(/\/\/\s*IMAGE_SPEC:[^\n]*/g, '');

  console.log('  ✓ Slides: 12 | Images specified: ' + imageSpecs.length);
  return { code: code, imageSpecs: imageSpecs };
}

// ═══ Step 2: Generate images (first from prompt, rest from reference) ═══
async function generateImages(imageSpecs) {
  console.log('\n[2/3] Generating ' + imageSpecs.length + ' images...');
  var results = {};

  if (imageSpecs.length === 0) return results;

  // First image: generate from prompt
  var firstSpec = imageSpecs[0];
  console.log('  [1/' + imageSpecs.length + '] Slide ' + firstSpec.slide + ' (base image)...');

  var firstImage = await callImageAPI(firstSpec.prompt + '. Professional architectural photography, modern luxury building, high quality, no text.');
  if (firstImage) {
    results[firstSpec.slide] = { data: firstImage, x: firstSpec.x, y: firstSpec.y, w: firstSpec.w, h: firstSpec.h };
    console.log('    ✓ Base image created');

    // Remaining images: use first image as reference
    for (var i = 1; i < imageSpecs.length; i++) {
      var spec = imageSpecs[i];
      console.log('  [' + (i + 1) + '/' + imageSpecs.length + '] Slide ' + spec.slide + ' (variant)...');

      var variantImage = await callImageAPIWithReference(firstImage, spec.prompt + '. Same building style, same architectural identity, professional photography, no text.');
      if (variantImage) {
        results[spec.slide] = { data: variantImage, x: spec.x, y: spec.y, w: spec.w, h: spec.h };
        console.log('    ✓ Variant created');
      } else {
        results[spec.slide] = { data: firstImage, x: spec.x, y: spec.y, w: spec.w, h: spec.h };
        console.log('    ✓ Used base image');
      }

      await new Promise(function(r) { setTimeout(r, 1000); });
    }
  } else {
    console.log('    ⚠ Failed to create base image');
  }

  return results;
}

async function callImageAPI(prompt) {
  try {
    var controller = new AbortController();
    var timeout = setTimeout(function() { controller.abort(); }, 90000);

    var response = await fetch(OPENROUTER_BASE + '/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization': 'Bearer ' + OPENROUTER_KEY,
        'Content-Type': 'application/json',
        'HTTP-Referer': 'https://github.com',
        'X-Title': 'PPTX Generator'
      },
      body: JSON.stringify({
        model: IMAGE_MODEL,
        messages: [{ role: 'user', content: prompt }]
      }),
      signal: controller.signal
    });

    clearTimeout(timeout);
    var data = await response.json();

    if (data.choices && data.choices[0] && data.choices[0].message.images) {
      var imgs = data.choices[0].message.images;
      if (imgs.length > 0 && imgs[0].image_url && imgs[0].image_url.url) {
        return imgs[0].image_url.url;
      }
    }
  } catch(e) {
    console.error('    API Error: ' + e.message);
  }
  return null;
}

async function callImageAPIWithReference(referenceImageBase64, prompt) {
  try {
    var controller = new AbortController();
    var timeout = setTimeout(function() { controller.abort(); }, 90000);

    var response = await fetch(OPENROUTER_BASE + '/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization': 'Bearer ' + OPENROUTER_KEY,
        'Content-Type': 'application/json',
        'HTTP-Referer': 'https://github.com',
        'X-Title': 'PPTX Generator'
      },
      body: JSON.stringify({
        model: IMAGE_MODEL,
        messages: [
          {
            role: 'user',
            content: [
              { type: 'text', text: prompt },
              { type: 'image_url', image_url: { url: referenceImageBase64 } }
            ]
          }
        ]
      }),
      signal: controller.signal
    });

    clearTimeout(timeout);
    var data = await response.json();

    if (data.choices && data.choices[0] && data.choices[0].message.images) {
      var imgs = data.choices[0].message.images;
      if (imgs.length > 0 && imgs[0].image_url && imgs[0].image_url.url) {
        return imgs[0].image_url.url;
      }
    }
  } catch(e) {
    console.error('    API Error: ' + e.message);
  }
  return null;
}

// ═══ Step 3: Merge and run ═══
async function main() {
  var topic = process.argv[2];
  var dataFile = process.argv[3];

  if (!topic) {
    console.log('\nUsage: node glm-designer.js "topic" [data.json]\n');
    process.exit(1);
  }

  console.log('═══════════════════════════════════════');
  console.log('  GLM 5.1 + Gemini Flash v2');
  console.log('═══════════════════════════════════════');
  console.log('  Topic: ' + topic);

  var projectData = null;
  if (dataFile && fs.existsSync(dataFile)) {
    projectData = JSON.parse(fs.readFileSync(dataFile, 'utf8'));
  }

  try {
    // 1. GLM generates code + image specs
    var result = await generateWithGLM(topic, projectData);

    // 2. Generate images based on specs
    var images = {};
    if (result.imageSpecs.length > 0) {
      images = await generateImages(result.imageSpecs);
    }

    // 3. Inject images into code at specified positions
    var outName = 'presentation_' + Date.now() + '.pptx';
    var code = result.code.replace(/presentation_[0-9]+\.pptx/g, outName);

    // Inject images before writeFile
    var imageBlock = '\n// === INJECTED IMAGES ===\n';
    for (var slideNum in images) {
      var img = images[slideNum];
      imageBlock += 'pptx.slides[' + (parseInt(slideNum) - 1) + '].addImage({ data: "' + img.data + '", x: ' + img.x + ', y: ' + img.y + ', w: ' + img.w + ', h: ' + img.h + ' });\n';
    }

    code = code.replace(/pptx\.writeFile/, imageBlock + '\npptx.writeFile');

    var fullCode = `
var logo = '${logoBase64}';
var projectData = ${JSON.stringify(projectData || {})};

${code}
`;

    var scriptPath = path.join(OUTPUT_DIR, '_generated_script.js');
    fs.writeFileSync(scriptPath, fullCode);

    console.log('\n[3/3] Running final presentation...');
    execSync('node ' + scriptPath, { stdio: 'inherit', cwd: __dirname });

    console.log('\n═══════════════════════════════════════');
    console.log('  DONE!');
    console.log('═══════════════════════════════════════\n');

  } catch (err) {
    console.error('\nError:', err.message);
    process.exit(1);
  }
}

main();
