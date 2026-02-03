#!/usr/bin/env python
"""
Generate Monthly Achievements Report with actual data from database
Usage: python generate_monthly_report.py [month] [year]
Example: python generate_monthly_report.py 12 2025
"""

import os
import sys
import django
from datetime import datetime, timedelta
from calendar import monthrange

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myProject.settings')
django.setup()

from django.utils import timezone
from django.db.models import Count, Q
from myApp.models import (
    Insight, CaseStudy, Service, FormSubmission,
    MediaAsset, TeamMember, ContentVersion
)

def get_month_range(month=None, year=None):
    """Get start and end dates for a given month"""
    now = timezone.now()
    if month is None:
        month = now.month - 1 if now.month > 1 else 12
    if year is None:
        year = now.year if now.month > 1 else now.year - 1
        if month == 12 and now.month == 1:
            year = now.year - 1
    
    # Get first and last day of the month
    first_day = datetime(year, month, 1, tzinfo=timezone.get_current_timezone())
    last_day_num = monthrange(year, month)[1]
    last_day = datetime(year, month, last_day_num, 23, 59, 59, tzinfo=timezone.get_current_timezone())
    
    return first_day, last_day, month, year

def generate_report(month=None, year=None):
    """Generate the monthly report with actual data"""
    
    start_date, end_date, report_month, report_year = get_month_range(month, year)
    month_name = datetime(report_year, report_month, 1).strftime('%B')
    
    print(f"\n{'='*60}")
    print(f"Generating Monthly Report for {month_name} {report_year}")
    print(f"Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    print(f"{'='*60}\n")
    
    # 1. INSIGHTS DATA
    print("📝 Gathering Insights Data...")
    insights_created = Insight.objects.filter(created_at__gte=start_date, created_at__lte=end_date)
    insights_published = insights_created.filter(published=True)
    
    insights_by_service = insights_created.values('service__title').annotate(count=Count('id'))
    
    print(f"  - Total Insights Created: {insights_created.count()}")
    print(f"  - Published: {insights_published.count()}")
    print(f"  - By Service:")
    for item in insights_by_service:
        print(f"    • {item['service__title']}: {item['count']}")
    
    # 2. CASE STUDIES DATA
    print("\n📊 Gathering Case Studies Data...")
    case_studies_created = CaseStudy.objects.filter(created_at__gte=start_date, created_at__lte=end_date)
    case_studies_by_service = case_studies_created.values('service__title').annotate(count=Count('id'))
    
    print(f"  - Total Case Studies Created: {case_studies_created.count()}")
    print(f"  - By Service:")
    for item in case_studies_by_service:
        print(f"    • {item['service__title']}: {item['count']}")
    
    # 3. FORM SUBMISSIONS DATA
    print("\n📧 Gathering Form Submissions Data...")
    submissions = FormSubmission.objects.filter(submitted_at__gte=start_date, submitted_at__lte=end_date)
    submissions_by_service = submissions.values('service').annotate(count=Count('id'))
    
    print(f"  - Total Submissions: {submissions.count()}")
    print(f"  - By Service:")
    for item in submissions_by_service:
        service_name = item['service'] if item['service'] else 'General'
        print(f"    • {service_name}: {item['count']}")
    
    # 4. MEDIA ASSETS DATA
    print("\n🖼️  Gathering Media Assets Data...")
    media_created = MediaAsset.objects.filter(created_at__gte=start_date, created_at__lte=end_date)
    print(f"  - Total Media Assets Uploaded: {media_created.count()}")
    
    # 5. SERVICES DATA
    print("\n🏗️  Gathering Services Data...")
    total_services = Service.objects.filter(is_active=True).count()
    print(f"  - Active Services: {total_services}")
    
    # 6. TOTAL COUNTS (All Time)
    print("\n📈 Total Counts (All Time):")
    print(f"  - Total Insights: {Insight.objects.filter(published=True, is_active=True).count()}")
    print(f"  - Total Case Studies: {CaseStudy.objects.count()}")
    print(f"  - Total Form Submissions: {FormSubmission.objects.count()}")
    print(f"  - Total Media Assets: {MediaAsset.objects.filter(is_active=True).count()}")
    
    # Generate report content
    report_content = f"""# Hammer Services - Monthly Achievements Report

**Report Period:** {month_name} {report_year}  
**Generated:** {timezone.now().strftime('%B %d, %Y at %I:%M %p')}  
**Website:** https://www.hammer-services.com

---

## 📊 Executive Summary

This report outlines the key achievements and performance metrics for Hammer Services during {month_name} {report_year}.

### Key Metrics
- **New Insights Published:** {insights_published.count()}
- **New Case Studies Added:** {case_studies_created.count()}
- **Contact Form Submissions:** {submissions.count()}
- **Media Assets Uploaded:** {media_created.count()}

---

## 📈 Detailed Achievements

### 1. Content Development

#### Insights/Blog Posts
- **Total Insights Created:** {insights_created.count()}
- **Published Insights:** {insights_published.count()}
- **Unpublished/Draft:** {insights_created.count() - insights_published.count()}

**Insights by Service:**
"""
    
    for item in insights_by_service:
        report_content += f"- {item['service__title']}: {item['count']}\n"
    
    report_content += f"""
**Notable Articles Published:**
"""
    
    for insight in insights_published[:10]:  # Top 10
        report_content += f"""
1. **{insight.title}**
   - Service: {insight.service.title}
   - Published: {insight.published_at.strftime('%B %d, %Y') if insight.published_at else 'N/A'}
   - Author: {insight.author.get_full_name() if insight.author else 'N/A'}
   - URL: https://www.hammer-services.com{insight.get_absolute_url()}
"""
    
    report_content += f"""
#### Case Studies
- **New Case Studies Added:** {case_studies_created.count()}

**Case Studies by Service:**
"""
    
    for item in case_studies_by_service:
        report_content += f"- {item['service__title']}: {item['count']}\n"
    
    report_content += f"""
**New Projects Added:**
"""
    
    for case_study in case_studies_created[:10]:  # Top 10
        completion = case_study.completion_date.strftime('%B %Y') if case_study.completion_date else 'N/A'
        report_content += f"""
1. **{case_study.title}**
   - Service: {case_study.service.title}
   - Completion Date: {completion}
   - Scope: {case_study.scope or 'N/A'}
   - Status: {case_study.status_label or 'N/A'}
"""
    
    report_content += f"""
### 2. User Engagement

#### Contact Form Submissions
- **Total Submissions:** {submissions.count()}
- **Average per Day:** {submissions.count() / max(1, (end_date - start_date).days):.1f}

**Service Inquiries Breakdown:**
"""
    
    for item in submissions_by_service:
        service_name = item['service'] if item['service'] else 'General'
        report_content += f"- {service_name}: {item['count']}\n"
    
    if submissions.count() > 0:
        report_content += f"""
**Recent Submissions (Last 10):**
"""
        for submission in submissions[:10]:
            report_content += f"""
- **{submission.name}** ({submission.email})
  - Service: {submission.service or 'General'}
  - Date: {submission.submitted_at.strftime('%B %d, %Y at %I:%M %p')}
  - Message Preview: {submission.message_preview[:100]}...
"""
    
    report_content += f"""
### 3. Media & Assets

#### Media Assets
- **Total Assets Uploaded:** {media_created.count()}
- **Active Assets (All Time):** {MediaAsset.objects.filter(is_active=True).count()}

---

## 📊 Overall Statistics (All Time)

- **Total Published Insights:** {Insight.objects.filter(published=True, is_active=True).count()}
- **Total Case Studies:** {CaseStudy.objects.count()}
- **Total Form Submissions:** {FormSubmission.objects.count()}
- **Total Active Services:** {Service.objects.filter(is_active=True).count()}
- **Total Media Assets:** {MediaAsset.objects.filter(is_active=True).count()}

---

## 🔗 External Backlinks Report

**Note:** Backlink data is not stored in the database. Please manually add backlink information from:
- Google Search Console (Links section)
- SEO tools (Ahrefs, SEMrush, Moz)
- Manual tracking records

See `BACKLINKS_LIST.md` for the backlinks template.

---

## 📝 Notes

- Report generated automatically from database records
- Dates are based on creation timestamps
- Backlinks must be added manually as they are not tracked in the database
- For analytics data (visits, page views, etc.), please check Google Analytics

---

**Report Generated:** {timezone.now().strftime('%B %d, %Y at %I:%M %p')}  
**Data Period:** {start_date.strftime('%B %d, %Y')} to {end_date.strftime('%B %d, %Y')}

*This report is generated automatically from the database. For additional metrics, please check Google Analytics and SEO tools.*
"""
    
    # Save report
    filename = f"MONTHLY_REPORT_{month_name}_{report_year}.md"
    filepath = os.path.join(os.path.dirname(os.path.dirname(__file__)), filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"\n✅ Report generated successfully!")
    print(f"📄 Saved to: {filepath}")
    print(f"\n📊 Summary:")
    print(f"   - Insights Created: {insights_created.count()}")
    print(f"   - Case Studies Created: {case_studies_created.count()}")
    print(f"   - Form Submissions: {submissions.count()}")
    print(f"   - Media Assets: {media_created.count()}")
    
    return filepath

if __name__ == '__main__':
    import sys
    
    month = None
    year = None
    
    if len(sys.argv) > 1:
        try:
            month = int(sys.argv[1])
        except ValueError:
            print("Error: Month must be a number (1-12)")
            sys.exit(1)
    
    if len(sys.argv) > 2:
        try:
            year = int(sys.argv[2])
        except ValueError:
            print("Error: Year must be a number")
            sys.exit(1)
    
    try:
        generate_report(month, year)
    except Exception as e:
        print(f"❌ Error generating report: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


