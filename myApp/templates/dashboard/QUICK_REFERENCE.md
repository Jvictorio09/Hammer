# Insight Form Editor - Quick Reference Guide

## 🎯 Core Concepts

### Layout Structure
```
Command Bar (Fixed Top)
├─ Left: Navigation + Title
├─ Center: Save Status
└─ Right: Preview + Publish

3-Column Layout
├─ Left (20%): Status Sidebar (Cards)
├─ Center (60%): Writing Zone (Editor)
└─ Right (20%): Navigation Sidebar
```

### Key Ratios
- **Left Sidebar**: 20% width
- **Editor Zone**: 60% width (max-width: 65ch for text)
- **Right Sidebar**: 20% width

---

## 🏗️ Essential Code Snippets

### 1. Base Template Override
```css
/* Hide base sidebar */
body > div.mx-auto > div.grid > aside {
  display: none !important;
}

/* Full width */
body > div.mx-auto { 
  max-width: 100% !important; 
  padding: 0 !important; 
}
```

### 2. 3-Column Layout
```html
<div class="h-screen flex flex-col">
  <!-- Command Bar -->
  <div class="sticky top-0 z-50 bg-white border-b">
    <!-- Content -->
  </div>
  
  <!-- 3 Columns -->
  <div class="flex-1 flex overflow-hidden">
    <aside class="w-[20%] bg-gray-50 border-r overflow-y-auto">
      <!-- Left sidebar -->
    </aside>
    <main class="w-[60%] bg-white border-x overflow-y-auto">
      <!-- Editor -->
    </main>
    <aside class="w-[20%] bg-white border-l overflow-y-auto">
      <!-- Right sidebar -->
    </aside>
  </div>
</div>
```

### 3. Editor.js Initialization
```javascript
const editor = new EditorJS({
  holder: 'editorHost',
  data: initialData,
  tools: {
    paragraph: { inlineToolbar: ['bold', 'italic', 'link'] },
    header: { class: Header, inlineToolbar: true },
    // ... other tools
  },
  onChange: async () => {
    // Auto-save logic
  }
});
```

### 4. Auto-Save Pattern
```javascript
let saveTimeout;
let hasUnsavedChanges = false;

editor.onChange = async () => {
  hasUnsavedChanges = true;
  clearTimeout(saveTimeout);
  saveTimeout = setTimeout(async () => {
    const output = await editor.save();
    document.getElementById('blocksField').value = JSON.stringify(output);
  }, 1000);
};
```

### 5. Form Submission Handler
```javascript
form.addEventListener('submit', async function(e) {
  e.preventDefault();
  
  const output = await editor.save();
  document.getElementById('blocksField').value = JSON.stringify(output);
  
  form.submit();
});
```

### 6. Card Pattern (Sidebar)
```html
<div class="bg-white border border-gray-200 rounded-lg p-4">
  <h3 class="text-sm font-semibold text-gray-900 mb-3">Title</h3>
  <!-- Content -->
</div>
```

### 7. Modal Pattern
```html
<div id="myModal" class="fixed inset-0 z-[100] hidden bg-gray-900/50">
  <div class="absolute inset-0 flex items-center justify-center">
    <div class="bg-white rounded-xl shadow-2xl max-w-4xl w-full">
      <!-- Modal content -->
    </div>
  </div>
</div>
```

### 8. Tab Switching
```javascript
function activateTab(activeTab, activeContent) {
  // Deactivate all
  allTabs.forEach(tab => tab.classList.remove('active'));
  allContents.forEach(content => content.classList.add('hidden'));
  
  // Activate selected
  activeTab.classList.add('active');
  activeContent.classList.remove('hidden');
}
```

---

## 🎨 Typography System

### Title Input
```css
font-size: 2.5rem;
font-weight: 700;
line-height: 1.2;
border: none;
```

### Excerpt Input
```css
font-size: 1.25rem;
line-height: 1.5;
color: #6b7280;
```

### Editor Text
```css
font-size: 18px;
line-height: 1.7;
max-width: 65ch;  /* Optimal reading width */
```

---

## 🔄 State Management

### Global Variables
```javascript
let editor;              // Editor.js instance
let saveTimeout;         // Debounce timer
let isSaving;            // Save lock
let hasUnsavedChanges;   // Dirty flag
let blocksSaved;         // Form submission flag
```

### Save Status States
- `draft` - Initial state
- `unsaved` - Changes detected
- `saving` - Currently saving
- `saved` - Successfully saved
- `error` - Save failed

---

## 🛠️ Common Patterns

### 1. Element Existence Check
```javascript
const element = document.getElementById('myElement');
if (element) {
  // Safe to use
}
```

### 2. Progress Bar Update
```javascript
progressBar.style.width = '50%';
statusText.textContent = 'Processing...';
```

### 3. Image Preview
```javascript
const img = new Image();
img.onload = () => {
  preview.src = url;
  preview.classList.remove('hidden');
};
img.onerror = () => {
  // Handle error
};
img.src = url;
```

### 4. Slug Generation
```javascript
function generateSlug(text) {
  return text
    .toLowerCase()
    .trim()
    .replace(/[^\w\s-]/g, '')
    .replace(/[\s_-]+/g, '-')
    .replace(/^-+|-+$/g, '');
}
```

### 5. CSRF Token
```javascript
function getCookie(name) {
  const m = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
  return m ? decodeURIComponent(m[2]) : null;
}
const CSRF = getCookie('csrftoken');
```

---

## 📋 Feature Checklist

When building a similar editor:

- [ ] 3-column layout structure
- [ ] Base template CSS overrides
- [ ] Editor.js integration
- [ ] Auto-save with debounce
- [ ] Form submission handler
- [ ] Save status indicator
- [ ] Card-based sidebar
- [ ] Modal system
- [ ] Progress feedback
- [ ] Error handling
- [ ] Image preview
- [ ] Title → slug generation
- [ ] Beforeunload warning

---

## 🎯 Design Principles

1. **Content First** - Writing zone is the hero
2. **Progressive Disclosure** - Show only what's needed
3. **Immediate Feedback** - Always show status
4. **Professional Polish** - Every detail matters

---

## 🚀 Quick Start

1. Copy the 3-column layout HTML
2. Add base template CSS overrides
3. Initialize Editor.js
4. Add auto-save logic
5. Handle form submission
6. Add your features as cards

---

## 💡 Pro Tips

- Use `65ch` max-width for optimal reading
- Debounce saves to 1 second
- Always await `editor.save()` before form submit
- Use flags to prevent submission loops
- Show progress at each step
- Handle errors gracefully
- Check element existence before use

---

**See `INSIGHT_FORM_DOCUMENTATION.md` for complete details.**

