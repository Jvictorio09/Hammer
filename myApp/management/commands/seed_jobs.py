#!/usr/bin/env python3
"""
Seed Job Postings for all departments

Usage:
  python manage.py seed_jobs
  python manage.py seed_jobs --wipe  # Delete existing jobs before seeding
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from myApp.models import JobPosting


class Command(BaseCommand):
    help = "Seed job postings for all departments"

    def add_arguments(self, parser):
        parser.add_argument(
            '--wipe',
            action='store_true',
            help='Delete existing job postings before seeding',
        )

    def handle(self, *args, **options):
        if options['wipe']:
            self.stdout.write(self.style.WARNING('Deleting existing job postings...'))
            JobPosting.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Deleted all existing job postings.'))

        jobs_data = [
            # Landscape Department
            {
                'title': 'Senior Landscape Designer',
                'department': 'Landscape',
                'description': '''We are seeking an experienced Senior Landscape Designer to lead our landscape design projects. 
The ideal candidate will have a strong portfolio of luxury residential and commercial projects, expertise in sustainable design practices, 
and the ability to work collaboratively with clients and project teams.

Key Responsibilities:
• Lead design development from concept to completion
• Create detailed landscape plans, sections, and specifications
• Collaborate with architects, engineers, and contractors
• Present design concepts to clients and stakeholders
• Manage multiple projects simultaneously
• Ensure designs meet local regulations and sustainability standards

Requirements:
• Bachelor's degree in Landscape Architecture or related field
• 5+ years of experience in landscape design
• Proficiency in AutoCAD, SketchUp, and Adobe Creative Suite
• Strong knowledge of local plant species and irrigation systems
• Excellent communication and presentation skills''',
                'is_active': True,
                'sort_order': 1,
            },
            {
                'title': 'Landscape Architect',
                'department': 'Landscape',
                'description': '''Join our team as a Landscape Architect to design and oversee the implementation of high-end landscape projects. 
You will work on luxury villas, commercial developments, and public spaces across Dubai.

Key Responsibilities:
• Develop comprehensive landscape architectural designs
• Prepare technical drawings and construction documents
• Coordinate with consultants and contractors
• Conduct site visits and inspections
• Ensure compliance with building codes and regulations
• Mentor junior designers

Requirements:
• Professional degree in Landscape Architecture
• Licensed Landscape Architect (preferred)
• 3+ years of professional experience
• Proficiency in AutoCAD, Revit, and 3D modeling software
• Strong technical knowledge of construction methods
• UAE driving license preferred''',
                'is_active': True,
                'sort_order': 2,
            },
            {
                'title': 'Horticulturist',
                'department': 'Landscape',
                'description': '''We are looking for a skilled Horticulturist to manage plant selection, care, and maintenance for our landscape projects. 
The role involves working closely with design teams to ensure plant selections are appropriate for Dubai's climate and project requirements.

Key Responsibilities:
• Select appropriate plant species for various projects
• Develop plant care and maintenance programs
• Conduct soil analysis and recommend treatments
• Manage plant procurement and quality control
• Provide technical guidance to installation teams
• Monitor plant health and implement pest/disease management

Requirements:
• Degree in Horticulture, Botany, or related field
• 3+ years of experience in horticulture
• Strong knowledge of Middle Eastern plant species
• Understanding of irrigation systems and water management
• Ability to work in outdoor conditions
• Valid UAE driving license''',
                'is_active': True,
                'sort_order': 3,
            },
            {
                'title': 'Landscape Project Manager',
                'department': 'Landscape',
                'description': '''Seeking an experienced Landscape Project Manager to oversee the execution of landscape projects from start to finish. 
You will coordinate teams, manage budgets, and ensure timely delivery of high-quality projects.

Key Responsibilities:
• Manage project timelines, budgets, and resources
• Coordinate with clients, consultants, and contractors
• Conduct regular site visits and progress meetings
• Ensure quality standards and safety compliance
• Handle project documentation and reporting
• Resolve issues and manage change orders

Requirements:
• Bachelor's degree in Landscape Architecture, Construction Management, or related field
• 5+ years of project management experience
• PMP certification (preferred)
• Strong leadership and communication skills
• Knowledge of construction processes and materials
• UAE driving license required''',
                'is_active': True,
                'sort_order': 4,
            },

            # Interior & Fit-Out Department
            {
                'title': 'Senior Interior Designer',
                'department': 'Interior & Fit-Out',
                'description': '''We are seeking a talented Senior Interior Designer to lead our luxury interior design projects. 
The ideal candidate will have experience designing high-end residential and commercial spaces with a focus on contemporary and modern aesthetics.

Key Responsibilities:
• Lead interior design projects from concept to completion
• Develop design concepts, mood boards, and presentations
• Create detailed drawings and specifications
• Source and specify furniture, fixtures, and finishes
• Collaborate with clients, architects, and contractors
• Manage design teams and junior designers

Requirements:
• Bachelor's degree in Interior Design or Architecture
• 6+ years of experience in luxury interior design
• Proficiency in AutoCAD, SketchUp, Revit, and Adobe Creative Suite
• Strong portfolio showcasing high-end residential projects
• Excellent client communication and presentation skills
• Knowledge of local suppliers and materials''',
                'is_active': True,
                'sort_order': 10,
            },
            {
                'title': 'Interior Design Consultant',
                'department': 'Interior & Fit-Out',
                'description': '''Join our team as an Interior Design Consultant to provide expert design advice and create stunning interior spaces. 
You will work directly with clients to understand their vision and translate it into beautiful, functional designs.

Key Responsibilities:
• Consult with clients to understand their needs and preferences
• Develop design proposals and presentations
• Create space plans and furniture layouts
• Select and specify materials, finishes, and furnishings
• Coordinate with suppliers and contractors
• Provide ongoing design support throughout projects

Requirements:
• Degree in Interior Design or related field
• 4+ years of interior design experience
• Strong creative and conceptual skills
• Excellent client relationship management
• Proficiency in design software (AutoCAD, SketchUp, etc.)
• Knowledge of luxury brands and materials''',
                'is_active': True,
                'sort_order': 11,
            },
            {
                'title': 'Fit-Out Project Manager',
                'department': 'Interior & Fit-Out',
                'description': '''We are looking for an experienced Fit-Out Project Manager to oversee interior fit-out projects. 
You will manage all aspects of project delivery including planning, coordination, quality control, and client relations.

Key Responsibilities:
• Manage fit-out projects from planning to handover
• Coordinate with design teams, contractors, and suppliers
• Monitor project progress, budgets, and schedules
• Conduct site inspections and quality checks
• Manage project documentation and reporting
• Ensure compliance with safety and building regulations

Requirements:
• Bachelor's degree in Construction Management, Architecture, or related field
• 5+ years of fit-out project management experience
• Strong knowledge of fit-out processes and materials
• Excellent organizational and leadership skills
• Ability to manage multiple projects simultaneously
• UAE driving license required''',
                'is_active': True,
                'sort_order': 12,
            },
            {
                'title': 'CAD Designer',
                'department': 'Interior & Fit-Out',
                'description': '''Seeking a skilled CAD Designer to create detailed technical drawings for interior design and fit-out projects. 
You will work closely with design teams to produce accurate construction documents.

Key Responsibilities:
• Create detailed CAD drawings and technical documentation
• Prepare shop drawings and as-built drawings
• Coordinate drawings with design and engineering teams
• Maintain drawing standards and file organization
• Update drawings based on site changes
• Assist in material take-offs and specifications

Requirements:
• Diploma or degree in Drafting, Architecture, or related field
• 3+ years of CAD drafting experience
• Proficiency in AutoCAD (required), Revit (preferred)
• Strong attention to detail and accuracy
• Knowledge of construction methods and materials
• Ability to work under tight deadlines''',
                'is_active': True,
                'sort_order': 13,
            },

            # Facility Management Department
            {
                'title': 'Facility Manager',
                'department': 'FM',
                'description': '''We are seeking an experienced Facility Manager to oversee the maintenance and operations of luxury residential and commercial properties. 
You will ensure properties are maintained to the highest standards and provide exceptional service to clients.

Key Responsibilities:
• Manage day-to-day facility operations and maintenance
• Develop and implement maintenance schedules and programs
• Coordinate with maintenance teams and service providers
• Manage facility budgets and expenses
• Ensure compliance with health, safety, and environmental regulations
• Handle client communications and service requests

Requirements:
• Bachelor's degree in Facility Management, Engineering, or related field
• 5+ years of facility management experience
• Strong knowledge of building systems (HVAC, electrical, plumbing)
• Excellent organizational and problem-solving skills
• Strong leadership and communication abilities
• UAE driving license required''',
                'is_active': True,
                'sort_order': 20,
            },
            {
                'title': 'Maintenance Supervisor',
                'department': 'FM',
                'description': '''Join our team as a Maintenance Supervisor to lead maintenance teams and ensure properties are well-maintained. 
You will oversee preventive and corrective maintenance activities across multiple properties.

Key Responsibilities:
• Supervise maintenance teams and technicians
• Schedule and coordinate maintenance activities
• Conduct regular property inspections
• Manage maintenance inventory and supplies
• Train and develop maintenance staff
• Ensure quality standards and safety compliance

Requirements:
• Technical diploma or degree in Engineering or related field
• 4+ years of maintenance supervision experience
• Strong technical knowledge of building systems
• Leadership and team management skills
• Ability to troubleshoot and resolve maintenance issues
• UAE driving license required''',
                'is_active': True,
                'sort_order': 21,
            },
            {
                'title': 'Property Manager',
                'department': 'FM',
                'description': '''We are looking for a Property Manager to manage luxury residential and commercial properties. 
You will be responsible for tenant relations, property maintenance, and ensuring properties operate smoothly.

Key Responsibilities:
• Manage tenant relations and communications
• Handle lease administration and renewals
• Coordinate property maintenance and repairs
• Conduct property inspections and assessments
• Manage property budgets and financial reporting
• Ensure compliance with property regulations

Requirements:
• Bachelor's degree in Real Estate, Business, or related field
• 3+ years of property management experience
• Strong customer service and communication skills
• Knowledge of property management software
• Ability to handle multiple properties simultaneously
• UAE driving license required''',
                'is_active': True,
                'sort_order': 22,
            },

            # Admin Department
            {
                'title': 'Administrative Assistant',
                'department': 'Admin',
                'description': '''We are seeking an organized and proactive Administrative Assistant to support our office operations. 
You will handle various administrative tasks and provide support to different departments.

Key Responsibilities:
• Handle general office administration and correspondence
• Manage schedules and appointments
• Prepare documents, reports, and presentations
• Coordinate meetings and events
• Maintain filing systems and records
• Assist with procurement and vendor management

Requirements:
• High school diploma or equivalent (Bachelor's preferred)
• 2+ years of administrative experience
• Proficiency in Microsoft Office Suite
• Excellent organizational and time management skills
• Strong communication skills (English required, Arabic preferred)
• Professional appearance and demeanor''',
                'is_active': True,
                'sort_order': 30,
            },
            {
                'title': 'Office Manager',
                'department': 'Admin',
                'description': '''Join our team as an Office Manager to oversee daily office operations and ensure smooth administrative functions. 
You will manage office facilities, coordinate administrative staff, and support various departments.

Key Responsibilities:
• Manage office operations and administrative functions
• Supervise administrative staff
• Coordinate office maintenance and supplies
• Handle vendor relations and contracts
• Manage office budgets and expenses
• Ensure compliance with office policies and procedures

Requirements:
• Bachelor's degree in Business Administration or related field
• 4+ years of office management experience
• Strong leadership and organizational skills
• Proficiency in office software and systems
• Excellent communication and interpersonal skills
• Ability to multitask and prioritize effectively''',
                'is_active': True,
                'sort_order': 31,
            },
            {
                'title': 'Executive Assistant',
                'department': 'Admin',
                'description': '''We are looking for an experienced Executive Assistant to provide high-level administrative support to senior management. 
You will handle confidential matters and coordinate executive activities.

Key Responsibilities:
• Provide comprehensive administrative support to executives
• Manage executive calendars and travel arrangements
• Prepare reports, presentations, and correspondence
• Coordinate meetings and events
• Handle confidential information with discretion
• Act as a liaison between executives and other departments

Requirements:
• Bachelor's degree preferred
• 5+ years of executive assistant experience
• Exceptional organizational and communication skills
• Proficiency in Microsoft Office Suite
• Ability to work independently and handle pressure
• Professional demeanor and confidentiality''',
                'is_active': True,
                'sort_order': 32,
            },

            # Finance Department
            {
                'title': 'Senior Accountant',
                'department': 'Finance',
                'description': '''We are seeking a qualified Senior Accountant to manage financial operations and reporting. 
You will be responsible for maintaining accurate financial records and preparing financial statements.

Key Responsibilities:
• Manage general ledger and financial records
• Prepare monthly, quarterly, and annual financial statements
• Conduct financial analysis and reporting
• Ensure compliance with accounting standards and regulations
• Coordinate with auditors and tax consultants
• Manage accounts payable and receivable

Requirements:
• Bachelor's degree in Accounting or Finance
• Professional accounting qualification (ACCA, CPA, or equivalent)
• 5+ years of accounting experience
• Proficiency in accounting software (QuickBooks, SAP, etc.)
• Strong analytical and problem-solving skills
• Knowledge of UAE tax regulations preferred''',
                'is_active': True,
                'sort_order': 40,
            },
            {
                'title': 'Financial Analyst',
                'department': 'Finance',
                'description': '''Join our finance team as a Financial Analyst to provide financial insights and support business decisions. 
You will analyze financial data, prepare forecasts, and support strategic planning.

Key Responsibilities:
• Analyze financial data and performance metrics
• Prepare financial forecasts and budgets
• Conduct variance analysis and reporting
• Support project financial analysis
• Prepare management reports and presentations
• Assist in financial planning and strategy

Requirements:
• Bachelor's degree in Finance, Accounting, or related field
• 3+ years of financial analysis experience
• Strong analytical and Excel skills
• Knowledge of financial modeling and forecasting
• Excellent communication and presentation skills
• Attention to detail and accuracy''',
                'is_active': True,
                'sort_order': 41,
            },
            {
                'title': 'Accounts Payable Specialist',
                'department': 'Finance',
                'description': '''We are looking for an Accounts Payable Specialist to manage vendor payments and accounts payable processes. 
You will ensure timely and accurate processing of invoices and payments.

Key Responsibilities:
• Process vendor invoices and payment requests
• Verify invoice accuracy and approvals
• Maintain accounts payable records
• Reconcile vendor statements
• Process payment runs and wire transfers
• Handle vendor inquiries and communications

Requirements:
• Diploma or degree in Accounting or Finance
• 2+ years of accounts payable experience
• Proficiency in accounting software
• Strong attention to detail
• Good organizational and time management skills
• Knowledge of payment processing systems''',
                'is_active': True,
                'sort_order': 42,
            },

            # Sales Department
            {
                'title': 'Sales Executive',
                'department': 'Sales',
                'description': '''We are seeking a dynamic Sales Executive to drive business growth and develop new client relationships. 
You will promote our services to potential clients and achieve sales targets.

Key Responsibilities:
• Identify and pursue new business opportunities
• Build and maintain client relationships
• Prepare and present proposals and quotations
• Negotiate contracts and close deals
• Achieve sales targets and KPIs
• Maintain CRM records and sales reports

Requirements:
• Bachelor's degree in Business, Marketing, or related field
• 3+ years of B2B sales experience
• Strong communication and negotiation skills
• Ability to build rapport with clients
• Self-motivated and target-driven
• UAE driving license required''',
                'is_active': True,
                'sort_order': 50,
            },
            {
                'title': 'Business Development Manager',
                'department': 'Sales',
                'description': '''Join our team as a Business Development Manager to develop strategic partnerships and expand our market presence. 
You will identify growth opportunities and build relationships with key stakeholders.

Key Responsibilities:
• Develop and execute business development strategies
• Identify and pursue new market opportunities
• Build strategic partnerships and alliances
• Conduct market research and analysis
• Represent company at industry events
• Prepare business proposals and presentations

Requirements:
• Bachelor's degree in Business, Marketing, or related field
• 5+ years of business development experience
• Strong strategic thinking and analytical skills
• Excellent networking and relationship-building abilities
• Experience in construction/design industry preferred
• UAE driving license required''',
                'is_active': True,
                'sort_order': 51,
            },
            {
                'title': 'Client Relations Manager',
                'department': 'Sales',
                'description': '''We are looking for a Client Relations Manager to maintain and strengthen relationships with existing clients. 
You will ensure client satisfaction and identify opportunities for additional services.

Key Responsibilities:
• Maintain relationships with existing clients
• Conduct regular client meetings and check-ins
• Address client concerns and resolve issues
• Identify upselling and cross-selling opportunities
• Gather client feedback and improve services
• Coordinate with project teams to ensure client satisfaction

Requirements:
• Bachelor's degree in Business, Marketing, or related field
• 4+ years of client relations or account management experience
• Excellent communication and interpersonal skills
• Strong problem-solving and conflict resolution abilities
• Customer-focused mindset
• UAE driving license required''',
                'is_active': True,
                'sort_order': 52,
            },
        ]

        created_count = 0
        updated_count = 0

        with transaction.atomic():
            for job_data in jobs_data:
                job, created = JobPosting.objects.update_or_create(
                    title=job_data['title'],
                    defaults={
                        'department': job_data['department'],
                        'description': job_data['description'],
                        'is_active': job_data['is_active'],
                        'sort_order': job_data['sort_order'],
                    }
                )
                if created:
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ Created: {job.title} ({job.department})')
                    )
                else:
                    updated_count += 1
                    self.stdout.write(
                        self.style.WARNING(f'↻ Updated: {job.title} ({job.department})')
                    )

        self.stdout.write(self.style.SUCCESS(
            f'\n✅ Successfully seeded {len(jobs_data)} job postings '
            f'({created_count} created, {updated_count} updated)'
        ))

