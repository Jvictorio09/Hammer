"""
Django management command to generate monthly achievements report
Usage: python manage.py generate_monthly_report [month] [year]
Example: python manage.py generate_monthly_report 12 2025
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Count
from datetime import datetime
from calendar import monthrange

from myApp.models import (
    Insight, CaseStudy, Service, FormSubmission,
    MediaAsset, TeamMember, ContentVersion
)


class Command(BaseCommand):
    help = 'Generate monthly achievements report with actual database data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--month',
            type=int,
            help='Month number (1-12). Defaults to previous month',
        )
        parser.add_argument(
            '--year',
            type=int,
            help='Year (e.g., 2025). Defaults to current year or previous year if month is December',
        )

    def handle(self, *args, **options):
        month = options.get('month')
        year = options.get('year')
        
        # Get month range
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
        
        month_name = datetime(year, month, 1).strftime('%B')
        
        self.stdout.write(self.style.SUCCESS(f'\n{"="*60}'))
        self.stdout.write(self.style.SUCCESS(f'Generating Monthly Report for {month_name} {year}'))
        self.stdout.write(self.style.SUCCESS(f'Period: {first_day.strftime("%Y-%m-%d")} to {last_day.strftime("%Y-%m-%d")}'))
        self.stdout.write(self.style.SUCCESS(f'{"="*60}\n'))
        
        # 1. INSIGHTS DATA
        self.stdout.write('📝 Gathering Insights Data...')
        insights_created = Insight.objects.filter(created_at__gte=first_day, created_at__lte=last_day)
        insights_published = insights_created.filter(published=True)
        
        insights_by_service = insights_created.values('service__title').annotate(count=Count('id'))
        
        self.stdout.write(f'  - Total Insights Created: {insights_created.count()}')
        self.stdout.write(f'  - Published: {insights_published.count()}')
        self.stdout.write(f'  - By Service:')
        for item in insights_by_service:
            self.stdout.write(f'    • {item["service__title"]}: {item["count"]}')
        
        # 2. CASE STUDIES DATA
        self.stdout.write('\n📊 Gathering Case Studies Data...')
        case_studies_created = CaseStudy.objects.filter(created_at__gte=first_day, created_at__lte=last_day)
        case_studies_by_service = case_studies_created.values('service__title').annotate(count=Count('id'))
        
        self.stdout.write(f'  - Total Case Studies Created: {case_studies_created.count()}')
        self.stdout.write(f'  - By Service:')
        for item in case_studies_by_service:
            self.stdout.write(f'    • {item["service__title"]}: {item["count"]}')
        
        # 3. FORM SUBMISSIONS DATA
        self.stdout.write('\n📧 Gathering Form Submissions Data...')
        submissions = FormSubmission.objects.filter(submitted_at__gte=first_day, submitted_at__lte=last_day)
        submissions_by_service = submissions.values('service').annotate(count=Count('id'))
        
        self.stdout.write(f'  - Total Submissions: {submissions.count()}')
        self.stdout.write(f'  - By Service:')
        for item in submissions_by_service:
            service_name = item['service'] if item['service'] else 'General'
            self.stdout.write(f'    • {service_name}: {item["count"]}')
        
        # 4. MEDIA ASSETS DATA
        self.stdout.write('\n🖼️  Gathering Media Assets Data...')
        media_created = MediaAsset.objects.filter(created_at__gte=first_day, created_at__lte=last_day)
        self.stdout.write(f'  - Total Media Assets Uploaded: {media_created.count()}')
        
        # 5. SERVICES DATA
        self.stdout.write('\n🏗️  Gathering Services Data...')
        total_services = Service.objects.filter(is_active=True).count()
        self.stdout.write(f'  - Active Services: {total_services}')
        
        # Generate report content
        report_content = self._generate_report_content(
            month_name, year, first_day, last_day,
            insights_created, insights_published, insights_by_service,
            case_studies_created, case_studies_by_service,
            submissions, submissions_by_service,
            media_created, total_services
        )
        
        # Save report
        import os
        filename = f'MONTHLY_REPORT_{month_name}_{year}.md'
        filepath = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        self.stdout.write(self.style.SUCCESS(f'\n✅ Report generated successfully!'))
        self.stdout.write(self.style.SUCCESS(f'📄 Saved to: {filepath}'))
        self.stdout.write(f'\n📊 Summary:')
        self.stdout.write(f'   - Insights Created: {insights_created.count()}')
        self.stdout.write(f'   - Case Studies Created: {case_studies_created.count()}')
        self.stdout.write(f'   - Form Submissions: {submissions.count()}')
        self.stdout.write(f'   - Media Assets: {media_created.count()}')

    def _generate_report_content(self, month_name, year, start_date, end_date,
                                insights_created, insights_published, insights_by_service,
                                case_studies_created, case_studies_by_service,
                                submissions, submissions_by_service,
                                media_created, total_services):
        """Generate the report markdown content"""
        
        report = f"""# Hammer Services - Monthly Achievements Report

**Report Period:** {month_name} {year}  
**Generated:** {timezone.now().strftime('%B %d, %Y at %I:%M %p')}  
**Website:** https://www.hammer-services.com

---

## 📊 Executive Summary

This report outlines the key achievements and performance metrics for Hammer Services during {month_name} {year}.

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
            report += f"- {item['service__title']}: {item['count']}\n"
        
        if not insights_by_service:
            report += "- No insights created this month\n"
        
        report += f"""
**Notable Articles Published:**
"""
        
        for insight in insights_published[:10]:  # Top 10
            author_name = insight.author.get_full_name() if insight.author and insight.author.get_full_name() else (insight.author.username if insight.author else 'N/A')
            pub_date = insight.published_at.strftime('%B %d, %Y') if insight.published_at else 'N/A'
            report += f"""
1. **{insight.title}**
   - Service: {insight.service.title}
   - Published: {pub_date}
   - Author: {author_name}
   - URL: https://www.hammer-services.com{insight.get_absolute_url()}
"""
        
        if insights_published.count() == 0:
            report += "\n*No insights were published this month.*\n"
        
        report += f"""
#### Case Studies
- **New Case Studies Added:** {case_studies_created.count()}

**Case Studies by Service:**
"""
        
        for item in case_studies_by_service:
            report += f"- {item['service__title']}: {item['count']}\n"
        
        if not case_studies_by_service:
            report += "- No case studies created this month\n"
        
        report += f"""
**New Projects Added:**
"""
        
        for case_study in case_studies_created[:10]:  # Top 10
            completion = case_study.completion_date.strftime('%B %Y') if case_study.completion_date else 'N/A'
            report += f"""
1. **{case_study.title}**
   - Service: {case_study.service.title}
   - Completion Date: {completion}
   - Scope: {case_study.scope or 'N/A'}
   - Status: {case_study.status_label or 'N/A'}
"""
        
        if case_studies_created.count() == 0:
            report += "\n*No case studies were added this month.*\n"
        
        report += f"""
### 2. User Engagement

#### Contact Form Submissions
- **Total Submissions:** {submissions.count()}
- **Average per Day:** {submissions.count() / max(1, (end_date - start_date).days):.1f}

**Service Inquiries Breakdown:**
"""
        
        for item in submissions_by_service:
            service_name = item['service'] if item['service'] else 'General'
            report += f"- {service_name}: {item['count']}\n"
        
        if not submissions_by_service:
            report += "- No submissions this month\n"
        
        if submissions.count() > 0:
            report += f"""
**Recent Submissions (Last 10):**
"""
            for submission in submissions[:10]:
                preview = submission.message_preview[:100] + '...' if submission.message_preview and len(submission.message_preview) > 100 else (submission.message_preview or 'N/A')
                report += f"""
- **{submission.name}** ({submission.email})
  - Service: {submission.service or 'General'}
  - Date: {submission.submitted_at.strftime('%B %d, %Y at %I:%M %p')}
  - Message Preview: {preview}
"""
        
        report += f"""
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
        
        return report

