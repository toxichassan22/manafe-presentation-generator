var express = require('express');
var path = require('path');
var fs = require('fs');
var { execSync, exec } = require('child_process');

var app = express();
var PORT = process.env.PORT || 3000;

// ═══ API Keys (same as glm-designer.js) ═══
var ZAI_KEY = process.env.ZAI_KEY;
var OPENROUTER_KEY = process.env.OPENROUTER_KEY;
var ZAI_BASE = 'https://api.z.ai/api/paas/v4';
var OPENROUTER_BASE = 'https://openrouter.ai/api/v1';
var GLM_MODEL = 'glm-5.1';
var IMAGE_MODEL = 'google/gemini-3.1-flash-image-preview';
var OUTPUT_DIR = path.join(__dirname, 'outputs');
var LOGO_PATH = path.join(__dirname, 'manafe-logo.png');
var USERS_DB_PATH = path.join(__dirname, 'users_db.json');

if (!fs.existsSync(OUTPUT_DIR)) fs.mkdirSync(OUTPUT_DIR, { recursive: true });

app.use(express.json({ limit: '50mb' }));
app.use(express.static(__dirname));
app.use('/outputs', express.static(path.join(__dirname, 'outputs')));

// ═══ User Database Schema & Helper Functions (JSON-based schema with ai_training_history) ═══
function loadUserDB() {
  if (fs.existsSync(USERS_DB_PATH)) {
    try {
      return JSON.parse(fs.readFileSync(USERS_DB_PATH, 'utf8'));
    } catch (e) {
      console.error('Error reading user database:', e);
    }
  }
  return { users: {} };
}

function saveUserDB(db) {
  try {
    fs.writeFileSync(USERS_DB_PATH, JSON.stringify(db, null, 2), 'utf8');
  } catch (e) {
    console.error('Error writing user database:', e);
  }
}

function getTrainingHistory(userId) {
  var db = loadUserDB();
  var user = db.users[userId || 'default_user'];
  return (user && user.ai_training_history) ? user.ai_training_history : [];
}

function saveTrainingHistory(userId, messages) {
  var db = loadUserDB();
  var id = userId || 'default_user';
  if (!db.users[id]) {
    db.users[id] = {};
  }
  db.users[id].ai_training_history = messages;
  saveUserDB(db);
}

// Helper to construct the messages list prepending training history to the API request to leverage Prefix Caching
function writeSystemPrombetBackup(messages, aiResponse) {
  try {
    var merged = JSON.parse(JSON.stringify(messages));
    if (aiResponse) {
      merged.push({ role: 'assistant', content: typeof aiResponse === 'string' ? aiResponse : JSON.stringify(aiResponse, null, 2) });
    }
    
    var backupContent = merged.map(function(m) {
      return "[" + m.role.toUpperCase() + "]:\n" + m.content;
    }).join('\n\n═══════════════════════════════════════\n\n');
    
    fs.writeFileSync(path.join(__dirname, 'systemprombet'), backupContent, 'utf8');
    fs.writeFileSync(path.join(__dirname, 'systemprombet.txt'), backupContent, 'utf8');
    fs.writeFileSync(path.join(__dirname, 'systemprombet.json'), JSON.stringify(merged, null, 2), 'utf8');
    
    // Auto-sync files to GitHub in background if token exists
    syncToGitHub();
  } catch (err) {
    console.error('Failed to write systemprombet backup:', err.message);
  }
}

function syncToGitHub() {
  var token = process.env.GITHUB_TOKEN;
  if (!token) {
    return; // Silently skip if no GitHub token is provided
  }
  
  var gitUrl = 'https://toxichassan22:' + token + '@github.com/toxichassan22/manafe-presentation-generator.git';
  
  // Check if git repo exists, if not initialize one (Docker container won't have .git)
  var initCmd = '';
  if (!fs.existsSync(path.join(__dirname, '.git'))) {
    initCmd = 'git init && git remote add origin ' + gitUrl + ' && git fetch origin main && git reset origin/main && ';
  }
  
  var cmd = initCmd +
            'git config user.email "toxichassan22@github.com" && ' +
            'git config user.name "toxichassan22" && ' +
            'git add -f systemprombet systemprombet.txt systemprombet.json users_db.json && ' +
            'git diff --cached --quiet && echo "No changes to commit" || ' +
            '(git commit -m "Auto-save chat history and backup [bot]" && ' +
            'git push ' + gitUrl + ' HEAD:main)';
            
  exec(cmd, { cwd: __dirname }, function(err, stdout, stderr) {
    if (err) {
      console.error('[Git Auto-Save] Sync failed:', err.message);
      if (stderr) console.error('[Git Auto-Save] stderr:', stderr);
    } else {
      console.log('[Git Auto-Save] ' + (stdout || 'Synced successfully'));
    }
  });
}

function buildMessagesWithTraining(systemContent, currentMessages, userId) {
  var history = getTrainingHistory(userId || 'default_user');
  var merged = [];
  
  if (systemContent) {
    merged.push({ role: 'system', content: systemContent });
  }
  
  // Prepend training history messages for implicit context caching
  if (history && history.length > 0) {
    history.forEach(function(msg) {
      if (msg.role === 'user' || msg.role === 'assistant' || msg.role === 'system') {
        merged.push({ role: msg.role, content: msg.content });
      }
    });
  }
  
  // Append current prompt/messages
  currentMessages.forEach(function(msg) {
    merged.push(msg);
  });

  // Backup system prompt & conversation chat (pre-response)
  writeSystemPrombetBackup(merged, null);
  
  return merged;
}

// Compute Cache Status and Metrics from Z.ai API Response
function computeCacheAnalytics(responseJson, fallbackSessionId) {
  var usage = responseJson.usage;
  var cachedTokens = 0;
  var promptTokens = 0;
  var completionTokens = 0;
  var totalTokens = 0;
  
  if (usage) {
    promptTokens = usage.prompt_tokens || 0;
    completionTokens = usage.completion_tokens || 0;
    totalTokens = usage.total_tokens || 0;
    
    if (typeof usage.cached_tokens === 'number') {
      cachedTokens = usage.cached_tokens;
    } else if (usage.prompt_tokens_details && typeof usage.prompt_tokens_details.cached_tokens === 'number') {
      cachedTokens = usage.prompt_tokens_details.cached_tokens;
    }
  }
  
  var savingPercentage = 0;
  if (promptTokens > 0) {
    savingPercentage = parseFloat(((cachedTokens / promptTokens) * 100).toFixed(1));
  }
  
  var status = cachedTokens > 0 ? 'HIT' : 'MISS';
  var sessionId = responseJson.id || fallbackSessionId || 'sess_' + Math.random().toString(36).substring(2, 11);
  
  return {
    status: status,
    cached_tokens: cachedTokens,
    session_id: sessionId,
    saving_percentage: savingPercentage,
    prompt_tokens: promptTokens,
    completion_tokens: completionTokens,
    total_tokens: totalTokens
  };
}


// ═══════════════════════════════════════════════════════════════
//  EXISTING ENDPOINTS
// ═══════════════════════════════════════════════════════════════

// Serve project data
app.get('/api/project-data', function(req, res) {
  var dataPath = path.join(__dirname, 'project-data.json');
  if (fs.existsSync(dataPath)) {
    res.json(JSON.parse(fs.readFileSync(dataPath, 'utf8')));
  } else {
    res.json(null);
  }
});

// Generate presentation (existing - calls glm-designer.js)
app.post('/api/generate', function(req, res) {
  var topic = req.body.topic;
  if (!topic) {
    return res.status(400).json({ error: 'Topic is required' });
  }

  console.log('\n═══════════════════════════════════════');
  console.log('  Starting generation from web UI...');
  console.log('  Topic: ' + topic);
  console.log('═══════════════════════════════════════');

  try {
    var dataFile = path.join(__dirname, 'project-data.json');
    var cmd = 'node glm-designer.js "' + topic.replace(/"/g, '\\"') + '" ' + dataFile;
    var output = execSync(cmd, { 
      cwd: __dirname, 
      encoding: 'utf8', 
      timeout: 300000,
      stdio: ['pipe', 'pipe', 'pipe']
    });
    console.log(output);

    // Find the generated file
    var files = fs.readdirSync(path.join(__dirname, 'outputs'))
      .filter(function(f) { return f.endsWith('.pptx'); })
      .map(function(f) { 
        return { name: f, time: fs.statSync(path.join(__dirname, 'outputs', f)).mtime.getTime() }; 
      })
      .sort(function(a, b) { return b.time - a.time; });

    if (files.length > 0) {
      res.json({ 
        success: true, 
        file: files[0].name,
        downloadUrl: '/outputs/' + files[0].name
      });
    } else {
      res.json({ success: true, file: null, message: 'Generation completed but no file found' });
    }
  } catch (err) {
    console.error('Generation error:', err.message);
    res.status(500).json({ error: err.message });
  }
});

// List generated files
app.get('/api/files', function(req, res) {
  var outDir = path.join(__dirname, 'outputs');
  if (!fs.existsSync(outDir)) {
    return res.json([]);
  }
  var files = fs.readdirSync(outDir)
    .filter(function(f) { return f.endsWith('.pptx'); })
    .map(function(f) { 
      return { 
        name: f, 
        url: '/outputs/' + f,
        size: fs.statSync(path.join(outDir, f)).size,
        time: fs.statSync(path.join(outDir, f)).mtime
      }; 
    })
    .sort(function(a, b) { return new Date(b.time) - new Date(a.time); });
  res.json(files);
});

// ─────────────────────────────────────────────
//  AI Customization / Training History Endpoints
// ─────────────────────────────────────────────
app.post('/api/save-training', function(req, res) {
  var messages = req.body.messages || req.body.history;
  var userId = req.body.userId || 'default_user';
  if (!messages || !Array.isArray(messages)) {
    return res.status(400).json({ error: 'Messages array is required' });
  }
  
  try {
    saveTrainingHistory(userId, messages);
    writeSystemPrombetBackup(messages, null);
    console.log('[Training] Saved training history and backup files for user: ' + userId + ' (' + messages.length + ' messages)');
    res.json({ success: true, message: 'Training history and backup saved successfully' });
  } catch (err) {
    console.error('[Training] Save error:', err.message);
    res.status(500).json({ error: err.message });
  }
});

app.get('/api/get-training', function(req, res) {
  var userId = req.query.userId || 'default_user';
  try {
    var history = getTrainingHistory(userId);
    res.json({ success: true, messages: history, history: history });
  } catch (err) {
    console.error('[Training] Get error:', err.message);
    res.status(500).json({ error: err.message });
  }
});

// ═══════════════════════════════════════════════════════════════
//  NEW ENDPOINTS - Called by the main index.html frontend
// ═══════════════════════════════════════════════════════════════

// ─────────────────────────────────────────────
//  1. POST /api/generate-main-image
//     Generate the main cover image via Gemini Flash
// ─────────────────────────────────────────────
app.post('/api/generate-main-image', async function(req, res) {
  var prompt = req.body.prompt;
  var referenceImage = req.body.referenceImage;
  if (!prompt) {
    return res.status(400).json({ error: 'Prompt is required' });
  }

  console.log('\n[Image] Generating main cover image...');
  console.log('  Prompt: ' + prompt.substring(0, 100) + '...');

  try {
    var image;
    if (referenceImage) {
      console.log('  Using uploaded image as base reference for main image...');
      image = await callImageAPIWithReference(
        referenceImage,
        prompt + '. Professional architectural photography, modern luxury building, high quality, no text, no watermarks.'
      );
    } else {
      image = await callImageAPI(
        prompt + '. Professional architectural photography, modern luxury building, high quality, no text, no watermarks.'
      );
    }

    if (image) {
      console.log('  ✓ Main image generated successfully');
      res.json({ success: true, image: image });
    } else {
      console.log('  ⚠ No image returned, using placeholder');
      res.json({ success: false, error: 'No image generated', image: null });
    }
  } catch (err) {
    console.error('  ✗ Main image error:', err.message);
    res.status(500).json({ error: err.message });
  }
});

// ─────────────────────────────────────────────
//  2. POST /api/generate-images
//     Generate multiple AI images (mood board)
// ─────────────────────────────────────────────
app.post('/api/generate-images', async function(req, res) {
  var prompts = req.body.prompts;
  var referenceImage = req.body.referenceImage;
  if (!prompts || !Array.isArray(prompts) || prompts.length === 0) {
    return res.status(400).json({ error: 'Prompts array is required' });
  }

  console.log('\n[Images] Generating ' + prompts.length + ' mood board images...');

  try {
    var images = [];
    var baseReference = referenceImage;

    if (baseReference) {
      console.log('  ✓ Using uploaded main image as base reference for all generated images...');
      for (var i = 0; i < prompts.length; i++) {
        console.log('  [' + (i + 1) + '/' + prompts.length + '] Generating variant from reference...');
        var img = await callImageAPIWithReference(
          baseReference,
          prompts[i] + '. Same building style, same architectural identity, professional photography, no text.'
        );
        if (img) {
          images.push({ url: img, prompt: prompts[i] });
          console.log('    ✓ Variant created');
        } else {
          // fallback to standard generation or copy reference
          var fallback = await callImageAPI(prompts[i] + '. Professional architectural photography, high quality, no text.');
          images.push({ url: fallback || baseReference, prompt: prompts[i] });
          console.log('    ✓ Fallback created');
        }
        if (i < prompts.length - 1) {
          await new Promise(function(r) { setTimeout(r, 1500); });
        }
      }
    } else {
      // No reference image, generate first one independently and use it as reference for rest
      console.log('  [1/' + prompts.length + '] Base image...');
      var firstImage = await callImageAPI(
        prompts[0] + '. Professional architectural photography, modern luxury building, high quality, no text.'
      );
      if (firstImage) {
        images.push({ url: firstImage, prompt: prompts[0] });
        console.log('    ✓ Base image created');

        for (var i = 1; i < prompts.length; i++) {
          console.log('  [' + (i + 1) + '/' + prompts.length + '] Variant image...');
          var variant = await callImageAPIWithReference(
            firstImage,
            prompts[i] + '. Same building style, same architectural identity, professional photography, no text.'
          );
          if (variant) {
            images.push({ url: variant, prompt: prompts[i] });
            console.log('    ✓ Variant created');
          } else {
            images.push({ url: firstImage, prompt: prompts[i] });
            console.log('    ✓ Used base image as fallback');
          }
          await new Promise(function(r) { setTimeout(r, 1500); });
        }
      } else {
        // If first image fails, generate all independently
        for (var i = 0; i < prompts.length; i++) {
          console.log('  [' + (i + 1) + '/' + prompts.length + '] Independent image...');
          var img = await callImageAPI(
            prompts[i] + '. Professional architectural photography, high quality, no text.'
          );
          images.push({ url: img, prompt: prompts[i] });
          if (i < prompts.length - 1) {
            await new Promise(function(r) { setTimeout(r, 1500); });
          }
        }
      }
    }

    console.log('  ✓ Generated ' + images.filter(function(x) { return x.url; }).length + '/' + prompts.length + ' images');
    res.json({ success: true, images: images });
  } catch (err) {
    console.error('  ✗ Images error:', err.message);
    res.status(500).json({ error: err.message });
  }
});

// ─────────────────────────────────────────────
//  3. POST /api/edit-deck-data
//     AI-powered editing of project form data
// ─────────────────────────────────────────────
app.post('/api/edit-deck-data', async function(req, res) {
  var editRequest = req.body.request;
  var projectData = req.body.data;

  if (!editRequest) {
    return res.status(400).json({ error: 'Edit request is required' });
  }

  console.log('\n[Edit] AI deck data edit...');
  console.log('  Request: ' + editRequest.substring(0, 100));

  try {
    var systemPrompt = `You are a professional investment project data editor for "منافع الاقتصادية" (Manafe).
The user will give you a request to modify project data fields. You must return the COMPLETE modified data as JSON.

RULES:
- Return ONLY valid JSON, no markdown, no code blocks
- Keep all existing fields intact unless the user specifically asks to change them
- For array fields (locationFeatures, projectFeatures, investmentHighlights, risks, components, timelineRows), maintain the same structure
- Use Arabic text when editing Arabic fields
- Make smart improvements based on the user's request
- Return the FULL data object with all fields`;

    var userMessage = 'PROJECT DATA:\n' + JSON.stringify(projectData, null, 2) + '\n\nEDIT REQUEST:\n' + editRequest;
    var promptMessages = buildMessagesWithTraining(
      systemPrompt,
      [{ role: 'user', content: userMessage }]
    );

    var response = await fetch(ZAI_BASE + '/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization': 'Bearer ' + ZAI_KEY,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        model: GLM_MODEL,
        messages: promptMessages,
        temperature: 0.7,
        max_tokens: 8000
      })
    });

    var data = await response.json();
    if (!data.choices || !data.choices[0]) {
      throw new Error('GLM failed: ' + JSON.stringify(data));
    }

    var cacheAnalytics = computeCacheAnalytics(data, 'edit_deck_' + Date.now());
    if (data.usage) {
      var u = data.usage;
      console.log('  ✓ Tokens: ' + u.total_tokens + ' | Cache: ' + cacheAnalytics.status + ' (' + cacheAnalytics.cached_tokens + ' tokens)');
    }

    var resultText = data.choices[0].message.content.trim();
    
    // Backup the full conversation (including the AI response)
    writeSystemPrombetBackup(promptMessages, resultText);

    // Try to extract JSON from the response
    var jsonMatch = resultText.match(/\{[\s\S]*\}/);
    if (jsonMatch) {
      var editedData = JSON.parse(jsonMatch[0]);
      console.log('  ✓ Data edited successfully');
      res.json({ success: true, data: editedData, cache_analytics: cacheAnalytics });
    } else {
      throw new Error('Could not parse AI response as JSON');
    }
  } catch (err) {
    console.error('  ✗ Edit error:', err.message);
    res.status(500).json({ error: err.message });
  }
});

// ─────────────────────────────────────────────
//  4. POST /api/ai-edit-slide
//     AI-powered single slide content editing
// ─────────────────────────────────────────────
app.post('/api/ai-edit-slide', async function(req, res) {
  var slideTitle = req.body.slideTitle;
  var slideContent = req.body.slideContent;
  var editRequest = req.body.editRequest;
  var projectData = req.body.projectData;

  if (!editRequest) {
    return res.status(400).json({ error: 'Edit request is required' });
  }

  console.log('\n[SlideEdit] Editing slide: ' + slideTitle);
  console.log('  Request: ' + editRequest.substring(0, 100));

  try {
    var systemPrompt = `You are a professional presentation content editor for "منافع الاقتصادية" (Manafe).
You edit individual slide content based on user requests.

RULES:
- Return a JSON object with: { "title": "slide title", "content": "new HTML content for the slide", "bullets": ["bullet1", "bullet2"] }
- The content should be HTML that works inside a div
- Keep the same style and language as the original
- Make smart improvements based on the user's request
- For investment project slides, maintain professional tone in Arabic
- Return ONLY valid JSON, no markdown`;

    var userMessage = 'SLIDE TITLE: ' + slideTitle + '\n\nCURRENT CONTENT:\n' + slideContent + '\n\nPROJECT DATA CONTEXT:\n' + JSON.stringify(projectData || {}, null, 2) + '\n\nEDIT REQUEST:\n' + editRequest;

    var promptMessages = buildMessagesWithTraining(
      systemPrompt,
      [{ role: 'user', content: userMessage }]
    );

    var response = await fetch(ZAI_BASE + '/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization': 'Bearer ' + ZAI_KEY,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        model: GLM_MODEL,
        messages: promptMessages,
        temperature: 0.7,
        max_tokens: 4000
      })
    });

    var data = await response.json();
    if (!data.choices || !data.choices[0]) {
      throw new Error('GLM failed: ' + JSON.stringify(data));
    }

    var cacheAnalytics = computeCacheAnalytics(data, 'edit_slide_' + Date.now());
    var resultText = data.choices[0].message.content.trim();

    // Backup the full conversation (including the AI response)
    writeSystemPrombetBackup(promptMessages, resultText);

    var jsonMatch = resultText.match(/\{[\s\S]*\}/);
    if (jsonMatch) {
      var edited = JSON.parse(jsonMatch[0]);
      console.log('  ✓ Slide edited successfully | Cache: ' + cacheAnalytics.status);
      res.json({ success: true, data: edited, cache_analytics: cacheAnalytics });
    } else {
      throw new Error('Could not parse AI response');
    }
  } catch (err) {
    console.error('  ✗ Slide edit error:', err.message);
    res.status(500).json({ error: err.message });
  }
});

// ─────────────────────────────────────────────
//  5. POST /api/ai-chat
//     General AI chat for slide editing
// ─────────────────────────────────────────────
app.post('/api/ai-chat', async function(req, res) {
  var message = req.body.message;
  var slidesData = req.body.slidesData;
  var currentSlideIdx = req.body.currentSlideIdx;
  var projectData = req.body.projectData;

  if (!message) {
    return res.status(400).json({ error: 'Message is required' });
  }

  console.log('\n[Chat] AI chat message...');
  console.log('  Message: ' + message.substring(0, 100));

  try {
    var systemPrompt = `You are a professional presentation editor AI for "منافع الاقتصادية" (Manafe).
You help users edit and improve their investment project presentations.

You can:
1. Edit slide content based on requests
2. Suggest improvements
3. Generate new content
4. Answer questions about the project

When the user asks you to edit something, respond with:
{ "action": "edit", "slideIdx": <number>, "changes": { "title": "new title if changed", "content": "new HTML content" } }

When the user asks a question or wants suggestions, respond with:
{ "action": "chat", "response": "your response in Arabic" }

Always respond in Arabic unless asked otherwise.
Return ONLY valid JSON.`;

    var contextData = {
      currentSlide: currentSlideIdx,
      message: message
    };
    if (slidesData) {
      contextData.slides = slidesData.map(function(s, i) {
        return { idx: i, title: s.title, contentPreview: (s.content || '').substring(0, 200) };
      });
    }

    var promptMessages = buildMessagesWithTraining(
      systemPrompt,
      [{ role: 'user', content: 'PROJECT DATA:\n' + JSON.stringify(projectData || {}, null, 2) + '\n\nSLIDES CONTEXT:\n' + JSON.stringify(contextData, null, 2) + '\n\nUSER MESSAGE:\n' + message }]
    );

    var response = await fetch(ZAI_BASE + '/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization': 'Bearer ' + ZAI_KEY,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        model: GLM_MODEL,
        messages: promptMessages,
        temperature: 0.7,
        max_tokens: 4000
      })
    });

    var data = await response.json();
    if (!data.choices || !data.choices[0]) {
      throw new Error('GLM failed: ' + JSON.stringify(data));
    }

    var cacheAnalytics = computeCacheAnalytics(data, 'chat_' + Date.now());
    var resultText = data.choices[0].message.content.trim();

    // Backup the full conversation (including the AI response)
    writeSystemPrombetBackup(promptMessages, resultText);

    var jsonMatch = resultText.match(/\{[\s\S]*\}/);
    if (jsonMatch) {
      var result = JSON.parse(jsonMatch[0]);
      console.log('  ✓ Chat response generated | Cache: ' + cacheAnalytics.status);
      res.json({ success: true, data: result, cache_analytics: cacheAnalytics });
    } else {
      // If not JSON, return as plain chat response
      res.json({ success: true, data: { action: 'chat', response: resultText }, cache_analytics: cacheAnalytics });
    }
  } catch (err) {
    console.error('  ✗ Chat error:', err.message);
    res.status(500).json({ error: err.message });
  }
});

// ─────────────────────────────────────────────
//  6. POST /api/generate-slide-image
//     Generate a single image for a specific slide
// ─────────────────────────────────────────────
app.post('/api/generate-slide-image', async function(req, res) {
  var prompt = req.body.prompt;
  var referenceImage = req.body.referenceImage;

  if (!prompt) {
    return res.status(400).json({ error: 'Prompt is required' });
  }

  console.log('\n[SlideImage] Generating slide image...');

  try {
    var image;
    if (referenceImage) {
      image = await callImageAPIWithReference(
        referenceImage,
        prompt + '. Same building style, professional architectural photography, high quality, no text.'
      );
    } else {
      image = await callImageAPI(
        prompt + '. Professional architectural photography, high quality, no text, no watermarks.'
      );
    }

    if (image) {
      console.log('  ✓ Slide image generated');
      res.json({ success: true, image: image });
    } else {
      res.json({ success: false, error: 'No image generated' });
    }
  } catch (err) {
    console.error('  ✗ Slide image error:', err.message);
    res.status(500).json({ error: err.message });
  }
});

// ─────────────────────────────────────────────
//  7. POST /api/generate-outline
//     GLM 5.1 generates outline structure (slide titles + bullets)
// ─────────────────────────────────────────────
app.post('/api/generate-outline', async function(req, res) {
  var projectData = req.body.projectData;

  console.log('\n[Outline] Generating outline structure via GLM 5.1...');

  try {
    var systemContent = 'أنت خبير في إعداد عروض تقديمية استثمارية احترافية لشركات العقارات والاستثمار في السعودية. مهمتك إنشاء هيكل (outline) للعرض التقديمي بناءً على بيانات المشروع.\n\nأعد النتيجة كـ JSON فقط بدون أي نص إضافي بالشكل:\n{\n  "slides": [\n    {\n      "title": "عنوان الشريحة",\n      "bullets": ["نقطة 1", "نقطة 2", "نقطة 3"]\n    }\n  ]\n}\n\nاجعل العرض يحتوي على 10-14 شريحة تشمل:\n1. غلاف المشروع\n2. الملخص التنفيذي\n3. فكرة المشروع والهيكلة\n4. مميزات الموقع (إذا تم توفير رابط قوقل ماب googleMapsLink في بيانات المشروع، يجب تضمينه كنقطة تحتوي على الرابط لعرضه)\n5. مميزات المشروع\n6. مكونات المشروع والمساحات\n7. الربح التشغيلي\n8. التكاليف\n9. الأرباح والتخارج\n10. الجدول الزمني\n11. المخاطر والتوصيات\n12. المود بورد\n13. شكراً وتواصل\n\nاجعل النقاط مختصرة واحترافية ومحددة. لا تكتب نصاً طويلاً - فقط نقاط ملخصة.';

    var response = await fetch(ZAI_BASE + '/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization': 'Bearer ' + ZAI_KEY,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        model: GLM_MODEL,
        messages: buildMessagesWithTraining(
          systemContent,
          [{ role: 'user', content: 'بيانات المشروع:\n' + JSON.stringify(projectData || {}, null, 2) }]
        ),
        temperature: 0.7,
        max_tokens: 4000
      })
    });

    var data = await response.json();
    if (!data.choices || !data.choices[0]) {
      throw new Error('GLM failed: ' + JSON.stringify(data));
    }

    var cacheAnalytics = computeCacheAnalytics(data, 'outline_' + Date.now());
    var resultText = data.choices[0].message.content.trim();
    var jsonMatch = resultText.match(/\{[\s\S]*\}/);
    if (jsonMatch) {
      var result = JSON.parse(jsonMatch[0]);
      console.log('  ✓ Outline generated: ' + (result.slides || []).length + ' slides | Cache: ' + cacheAnalytics.status);
      res.json({ success: true, outline: result.slides || [], cache_analytics: cacheAnalytics });
    } else {
      throw new Error('No JSON in GLM response');
    }
  } catch (err) {
    console.error('  ✗ Outline generation error:', err.message);
    res.status(500).json({ error: err.message });
  }
});

// ─────────────────────────────────────────────
//  7b. POST /api/generate-titles
//      Fast: returns just slide titles (no bullets)
// ─────────────────────────────────────────────
app.post('/api/generate-titles', async function(req, res) {
  var projectData = req.body.projectData;
  console.log('\n[Titles] Generating slide titles via GLM 5.1...');
  var startTime = Date.now();

  try {
    var systemContent = 'أنت خبير في العروض التقديمية الاستثمارية. أنشئ 10-13 عنوان شريحة مختصر واحترافي.\n\nأعد النتيجة كـ JSON فقط:\n{"titles": ["عنوان 1", "عنوان 2", ...]}\n\nالشرائح المطلوبة:\n1. غلاف المشروع\n2. الملخص التنفيذي\n3. فكرة المشروع\n4. مميزات الموقع\n5. مميزات المشروع\n6. مكونات المشروع\n7. الربح التشغيلي\n8. التكاليف\n9. الأرباح\n10. الجدول الزمني\n11. المخاطر\n12. شكراً';

    var response = await fetch(ZAI_BASE + '/chat/completions', {
      method: 'POST',
      headers: { 'Authorization': 'Bearer ' + ZAI_KEY, 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: GLM_MODEL,
        messages: buildMessagesWithTraining(
          systemContent,
          [{ role: 'user', content: 'بيانات المشروع:\n' + JSON.stringify(projectData || {}, null, 2) }]
        ),
        temperature: 0.7,
        max_tokens: 1500,
        thinking: { type: "disabled" }
      })
    });

    var data = await response.json();
    if (!data.choices || !data.choices[0]) throw new Error('GLM failed: ' + JSON.stringify(data));

    var cacheAnalytics = computeCacheAnalytics(data, 'titles_' + Date.now());
    var text = (data.choices[0].message.content || '').trim();
    var match = text.match(/\{[\s\S]*\}/);
    if (!match) throw new Error('No JSON in response');

    var result = JSON.parse(match[0]);
    var titles = result.titles || result.slides || [];
    console.log('  ✓ Got ' + titles.length + ' titles in ' + ((Date.now() - startTime) / 1000).toFixed(1) + 's | Cache: ' + cacheAnalytics.status);
    res.json({ success: true, titles: titles, cache_analytics: cacheAnalytics });
  } catch (err) {
    console.error('  ✗ Titles error:', err.message);
    res.status(500).json({ error: err.message });
  }
});

// ─────────────────────────────────────────────
//  7c. POST /api/generate-bullets
//      Returns bullets for multiple slides in parallel
// ─────────────────────────────────────────────
app.post('/api/generate-bullets', async function(req, res) {
  var projectData = req.body.projectData;
  var slides = req.body.slides || []; // [{index, title}, ...]

  console.log('\n[Bullets] Generating bullets for ' + slides.length + ' slides...');

  try {
    var promises = slides.map(function(slide) {
      var systemContent = 'أنت خبير في العروض التقديمية الاستثمارية. أنشئ 3-5 نقاط مختصرة واحترافية لهذه الشريحة. إذا كانت الشريحة هي "مميزات الموقع" وكان هناك رابط قوقل ماب (googleMapsLink) في بيانات المشروع، أضف نقطة تحتوي على رابط قوقل ماب المعطى بوضوح.\n\nأعد النتيجة كـ JSON فقط:\n{"bullets": ["نقطة 1", "نقطة 2", "نقطة 3"]}';
      var userContent = 'بيانات المشروع:\n' + JSON.stringify(projectData || {}, null, 2) + '\n\nعنوان الشريحة: ' + slide.title;

      return fetch(ZAI_BASE + '/chat/completions', {
        method: 'POST',
        headers: { 'Authorization': 'Bearer ' + ZAI_KEY, 'Content-Type': 'application/json' },
        body: JSON.stringify({
          model: GLM_MODEL,
          messages: buildMessagesWithTraining(
            systemContent,
            [{ role: 'user', content: userContent }]
          ),
          temperature: 0.7,
          max_tokens: 1000,
          thinking: { type: "disabled" }
        })
      }).then(function(r) { return r.json(); }).then(function(d) {
        var m = (d.choices && d.choices[0] && d.choices[0].message) ? d.choices[0].message : {};
        var text = (m.content || '').trim();
        var jm = text.match(/\{[\s\S]*\}/);
        var bullets = [];
        if (jm) { try { bullets = JSON.parse(jm[0]).bullets || []; } catch(e) {} }
        return { index: slide.index, title: slide.title, bullets: bullets, usage: d.usage, id: d.id };
      }).catch(function(err) {
        console.error('  ✗ Bullet error ' + slide.index + ':', err.message);
        return { index: slide.index, title: slide.title, bullets: [], usage: null, id: null };
      });
    });

    var results = await Promise.all(promises);
    results.sort(function(a, b) { return a.index - b.index; });

    // Consolidate caching analytics across parallel requests
    var totalPromptTokens = 0;
    var totalCachedTokens = 0;
    var totalCompletionTokens = 0;
    var totalTokensCount = 0;
    var sessionIds = [];

    results.forEach(function(r) {
      if (r.usage) {
        totalPromptTokens += r.usage.prompt_tokens || 0;
        totalCompletionTokens += r.usage.completion_tokens || 0;
        totalTokensCount += r.usage.total_tokens || 0;

        var cached = 0;
        if (typeof r.usage.cached_tokens === 'number') {
          cached = r.usage.cached_tokens;
        } else if (r.usage.prompt_tokens_details && typeof r.usage.prompt_tokens_details.cached_tokens === 'number') {
          cached = r.usage.prompt_tokens_details.cached_tokens;
        }
        totalCachedTokens += cached;
      }
      if (r.id) {
        sessionIds.push(r.id);
      }
      // Remove details to keep API clean
      delete r.usage;
      delete r.id;
    });

    var savingPercentage = 0;
    if (totalPromptTokens > 0) {
      savingPercentage = parseFloat(((totalCachedTokens / totalPromptTokens) * 100).toFixed(1));
    }

    var cacheAnalytics = {
      status: totalCachedTokens > 0 ? 'HIT' : 'MISS',
      cached_tokens: totalCachedTokens,
      session_id: sessionIds.length > 0 ? sessionIds[0] : 'bullets_' + Date.now(),
      saving_percentage: savingPercentage,
      prompt_tokens: totalPromptTokens,
      completion_tokens: totalCompletionTokens,
      total_tokens: totalTokensCount
    };

    console.log('  ✓ Got bullets for ' + results.length + ' slides | Cache: ' + cacheAnalytics.status + ' (' + cacheAnalytics.cached_tokens + ' tokens)');
    res.json({ success: true, slides: results, cache_analytics: cacheAnalytics });
  } catch (err) {
    console.error('  ✗ Bullets error:', err.message);
    res.status(500).json({ error: err.message });
  }
});

// ─────────────────────────────────────────────
//  8. POST /api/generate-content
//     GLM 5.1 writes full content for all slides
// ─────────────────────────────────────────────
app.post('/api/generate-content', async function(req, res) {
  var projectData = req.body.projectData;
  var outline = req.body.outline;

  console.log('\n[Content] Generating full slide content via GLM 5.1...');

  try {
    var systemContent = 'أنت كاتب محتوى احترافي للعروض التقديمية الاستثمارية. مهمتك كتابة محتوى كامل ومفصل لكل شريحة في العرض التقديمي. إذا كانت الشريحة هي مميزات الموقع وتم توفير رابط قوقل ماب googleMapsLink في بيانات المشروع، قم بإنشاء زر أو رابط تشعبي HTML واضح (باستخدام <a href="..." target="_blank">) لعرض موقع المشروع على قوقل ماب.\n\nأعد النتيجة كـ JSON فقط بدون أي نص إضافي بالشكل:\n{\n  "slides": [\n    {\n      "title": "عنوان الشريحة",\n      "content": "<div class=\\"ge-slide-title\\">العنوان</div><div class=\\"ge-slide-subtitle\\">العنوان الفرعي</div><div class=\\"ge-slide-body\\"><ul><li>نقطة 1</li><li>نقطة 2</li></ul></div>"\n    }\n  ]\n}\n\nكل شريحة يجب أن تحتوي على:\n- title: العنوان الرئيسي المختصر\n- content: HTML markup بتنسيق احترافي يستخدم CSS classes: ge-slide-title, ge-slide-subtitle, ge-slide-body, ge-slide-metrics, ge-metric, ge-metric-label, ge-metric-value\n\nاكتب محتوى عربي احترافي ومفصل. استخدم الأرقام والبيانات المالية من بيانات المشروع.';

    var response = await fetch(ZAI_BASE + '/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization': 'Bearer ' + ZAI_KEY,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        model: GLM_MODEL,
        messages: buildMessagesWithTraining(
          systemContent,
          [{ role: 'user', content: 'بيانات المشروع:\n' + JSON.stringify(projectData || {}, null, 2) + '\n\nهيكل العرض (Outline):\n' + JSON.stringify(outline || [], null, 2) }]
        ),
        temperature: 0.7,
        max_tokens: 8000
      })
    });

    var data = await response.json();
    if (!data.choices || !data.choices[0]) {
      throw new Error('GLM failed: ' + JSON.stringify(data));
    }

    var cacheAnalytics = computeCacheAnalytics(data, 'content_' + Date.now());
    var resultText = data.choices[0].message.content.trim();
    var jsonMatch = resultText.match(/\{[\s\S]*\}/);
    if (jsonMatch) {
      var result = JSON.parse(jsonMatch[0]);
      console.log('  ✓ Content generated for ' + (result.slides || []).length + ' slides | Cache: ' + cacheAnalytics.status);
      res.json({ success: true, slides: result.slides || [], cache_analytics: cacheAnalytics });
    } else {
      throw new Error('No JSON in GLM response');
    }
  } catch (err) {
    console.error('  ✗ Content generation error:', err.message);
    res.status(500).json({ error: err.message });
  }
});

// ─────────────────────────────────────────────
//  9. POST /api/organize-text
//     GLM 5.1 organizes raw text across slides
// ─────────────────────────────────────────────
app.post('/api/organize-text', async function(req, res) {
  var projectData = req.body.projectData;
  var rawText = req.body.rawText;
  var outline = req.body.outline;

  console.log('\n[Organize] Organizing text across slides via GLM 5.1...');

  try {
    var systemContent = 'أنت خبير في تنظيم المحتوى للعروض التقديمية. مهمتك تنظيم نص خام على شرائح العرض التقديمي حسب المحتوى المناسب لكل شريحة.\n\nأعد النتيجة كـ JSON فقط بدون أي نص إضافي بالشكل:\n{\n  "slides": [\n    {\n      "title": "عنوان الشريحة",\n      "bullets": ["نقطة 1 من النص", "نقطة 2 من النص"],\n      "missingInfo": "معلومات إضافية مطلوبة إن وُجدت"\n    }\n  ]\n}\n\nقواعد التنظيم:\n1. وزع محتوى النص على الشرائح المناسبة حسب الهيكل المحدد\n2. إذا كانت معلومات شريحة معينة غير مكتملة أو ناقصة، اذكرها في missingInfo\n3. احتفظ بالعناوين الأصلية للشرائح\n4. اجعل النقاط مختصرة ومنظمة\n5. لا تختلق معلومات - استخدم فقط ما يوجد في النص المكتوب\n6. إذا كان النص خالياً أو قصيراً جداً، اذكر ذلك في missingInfo';

    var response = await fetch(ZAI_BASE + '/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization': 'Bearer ' + ZAI_KEY,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        model: GLM_MODEL,
        messages: buildMessagesWithTraining(
          systemContent,
          [{ role: 'user', content: 'بيانات المشروع:\n' + JSON.stringify(projectData || {}, null, 2) + '\n\nهيكل العرض:\n' + JSON.stringify(outline || [], null, 2) + '\n\nالنص المكتوب يدوياً:\n' + (rawText || 'لا يوجد نص') }]
        ),
        temperature: 0.7,
        max_tokens: 6000
      })
    });

    var data = await response.json();
    if (!data.choices || !data.choices[0]) {
      throw new Error('GLM failed: ' + JSON.stringify(data));
    }

    var cacheAnalytics = computeCacheAnalytics(data, 'organize_' + Date.now());
    var resultText = data.choices[0].message.content.trim();
    var jsonMatch = resultText.match(/\{[\s\S]*\}/);
    if (jsonMatch) {
      var result = JSON.parse(jsonMatch[0]);
      console.log('  ✓ Text organized across ' + (result.slides || []).length + ' slides | Cache: ' + cacheAnalytics.status);
      res.json({ success: true, slides: result.slides || [], cache_analytics: cacheAnalytics });
    } else {
      throw new Error('No JSON in GLM response');
    }
  } catch (err) {
    console.error('  ✗ Organize text error:', err.message);
    res.status(500).json({ error: err.message });
  }
});

// ═══════════════════════════════════════════════════════════════
//  HELPER FUNCTIONS - Image Generation via OpenRouter/Gemini
// ═══════════════════════════════════════════════════════════════

async function callImageAPI(prompt) {
  try {
    var controller = new AbortController();
    var timeout = setTimeout(function() { controller.abort(); }, 120000);

    var response = await fetch(OPENROUTER_BASE + '/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization': 'Bearer ' + OPENROUTER_KEY,
        'Content-Type': 'application/json',
        'HTTP-Referer': 'https://github.com',
        'X-Title': 'Manafe PPTX Generator'
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
  } catch (e) {
    console.error('    Image API Error: ' + e.message);
  }
  return null;
}

async function callImageAPIWithReference(referenceImageBase64, prompt) {
  try {
    var controller = new AbortController();
    var timeout = setTimeout(function() { controller.abort(); }, 120000);

    var response = await fetch(OPENROUTER_BASE + '/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization': 'Bearer ' + OPENROUTER_KEY,
        'Content-Type': 'application/json',
        'HTTP-Referer': 'https://github.com',
        'X-Title': 'Manafe PPTX Generator'
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
  } catch (e) {
    console.error('    Image API Error: ' + e.message);
  }
  return null;
}

// ═══════════════════════════════════════════════════════════════
//  START SERVER
// ═══════════════════════════════════════════════════════════════

app.listen(PORT, function() {
  console.log('\n═══════════════════════════════════════');
  console.log('  🌐 Server running on port ' + PORT);
  console.log('  🔗 http://localhost:' + PORT);
  console.log('  📋 API Endpoints:');
  console.log('    GET  /api/project-data');
  console.log('    POST /api/generate');
  console.log('    GET  /api/files');
  console.log('    POST /api/generate-main-image');
  console.log('    POST /api/generate-images');
  console.log('    POST /api/generate-slide-image');
  console.log('    POST /api/edit-deck-data');
  console.log('    POST /api/ai-edit-slide');
  console.log('    POST /api/ai-chat');
  console.log('═══════════════════════════════════════\n');
});
