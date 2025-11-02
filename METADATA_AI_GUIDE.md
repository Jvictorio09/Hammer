# 🤖 AI-Powered Metadata Generation

Automated SEO metadata generation using OpenAI.

## 📋 Overview

Upload a CSV with URLs and get AI-generated, SEO-optimized metadata automatically.

## 🚀 How It Works

1. **Upload CSV**: Provide URLs in CSV format
2. **AI Analysis**: OpenAI analyzes each URL and context
3. **Auto-Generation**: Creates rich metadata including:
   - Meta Title (50-70 chars optimal)
   - Meta Description (150-160 chars optimal)
   - Meta Keywords (5-10 relevant keywords)

## 📝 CSV Format

Your CSV must have a URL column. The system accepts:

**Column Names (case-insensitive):**
- `Page URL`, `url_path`, `URL`, `Link`, or `Address`

**URL Formats:**
- Full URLs: `https://www.hammer-services.com/about/` ✅
- Paths: `/about/` ✅

**Example:**

```csv
Page URL,Page Name
https://www.hammer-services.com/,Home Page
https://www.hammer-services.com/about/,About Us
https://www.hammer-services.com/services/interior-design/,Interior Design Service
```

**Note:** Full URLs are automatically converted to paths. The system extracts just the path portion (`/about/`) from full URLs.

- **Page URL**: Required. Full URL or path
- **Page Name**: Optional. Human-readable page name for context (column can be named `page_name`, `Page Name`, `Name`, or `Title`)

## 🔑 Setup

### 1. Install OpenAI Library

```bash
pip install openai
```

### 2. Add API Key to .env

Add your OpenAI API key to your `.env` file:

```env
OPENAI_API_KEY=sk-your-api-key-here
```

### 3. Access Upload Page

Visit: `/dashboard/metadata/upload-csv/`

## 🎯 Usage

1. Click **"Upload CSV"** on the metadata list page
2. Select your CSV file
3. Choose AI generation (on/off)
4. Click **"Upload & Generate Metadata"**
5. Review results on the metadata list

## 🔧 Features

### AI Generation Mode
- Uses GPT-4o-mini for cost-effective generation
- Context-aware metadata based on URL path
- Dubai-specific, luxury-focused content
- Industry-optimized keywords

### Fallback Mode
- Basic metadata if AI unavailable
- No API costs
- Still creates usable SEO metadata

### Smart Processing
- Auto-detects page type from URL
- Infers keywords from context
- Maintains length constraints
- Skips duplicate URLs

## 📊 Example Output

**Input:**
```
url_path: /interior/luxury-villas/
page_name: Luxury Villa Interiors
```

**AI Output:**
```
TITLE: Luxury Villa Interior Design Dubai | Expert Residential Fit-Out | Hammer Group
DESCRIPTION: Transform your Dubai villa with luxurious interior design and residential fit-out services. Expert craftsmanship, premium finishes, and 20+ years of creating exceptional living spaces.
KEYWORDS: Dubai villa interiors, luxury home design, residential fit-out Dubai, custom interiors, luxury renovation
```

## ⚙️ Configuration

The AI prompt is optimized for:
- **Industry**: Luxury construction, landscaping, interior design
- **Location**: Dubai, UAE
- **Company**: Hammer Group
- **Style**: Premium, luxury, high-end
- **Experience**: 20+ years

## 💡 Tips

1. **Use Descriptive URLs**: Better URLs = better AI understanding
2. **Add Page Names**: Helps AI understand context
3. **Check Results**: Review and edit AI-generated metadata
4. **Batch Process**: Upload multiple URLs at once

## 🛡️ Safety

- AI generation uses GPT-4o-mini (cost-effective)
- Fallback ensures system always works
- Error handling for API failures
- No sensitive data sent to AI
- Configurable toggle for AI on/off

## 📖 See Also

- `metadata_sample.csv` - Example CSV file
- Standard metadata management in dashboard
- Manual metadata creation forms

---

**Ready to automate your SEO!** 🚀

