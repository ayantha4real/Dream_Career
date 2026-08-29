"""
Sri Lankan synthetic resume generator.

Produces realistic, locally contextualized resumes for ALL 24
career categories in the DreamCareer label space:

  - Sinhala / Tamil / English Sri Lankan names
  - Local cities and districts
  - Local employers, universities and qualifications
    (G.C.E. A/L, NVQ, SLIIT, NSBM, University of Moratuwa,
     CA Sri Lanka, CIMA, SLMC, ...)
  - +94 phone numbers

Output is strictly deduplicated:
  1. exact-duplicate removal on normalized text
  2. near-duplicate removal on skill-signature + role hash

Run:  venv\\Scripts\\python generate_synthetic_resumes.py
"""

import hashlib
import os
import random
import re

import pandas as pd

random.seed(2026)

OUTPUT_FILE = "datasets/processed/synthetic_resumes.csv"

PER_CATEGORY = 55


FIRST_NAMES = [
    "Nimal", "Kamal", "Sunil", "Anura", "Ruwan", "Tharindu", "Kavindu",
    "Dilshan", "Sahan", "Chamara", "Nuwan", "Pradeep", "Lasith", "Ishara",
    "Sanduni", "Dilini", "Hasini", "Amaya", "Nethmi", "Rashmi",
    "Thilini", "Chathurika", "Ayodya", "Shanika", "Irosha",
    "Ahilan", "Kajendran", "Thivya", "Niranjala", "Sathees",
    "Fathima", "Rizwana", "Mohamed", "Nusrath", "Zainab",
    "David", "Ryan", "Melissa", "Sheromi", "Yohan", "Rehan",
]

LAST_NAMES = [
    "Perera", "Fernando", "Silva", "Jayasuriya", "Wickramasinghe",
    "Bandara", "Rajapaksha", "Gunawardena", "Dissanayake", "Ekanayake",
    "Herath", "Weerasinghe", "Kumari", "Gamage", "Amarasinghe",
    "Fernandopulle", "Alwis", "Dharmasiri",
    "Rizwan", "Hameed", "Nazreen", "Careem",
    "Krishnan", "Sivakumar", "Rajendra", "Nadarajah",
    "Fernando", "De Silva", "Rodrigo", "Peiris",
]


CITIES = [
    "Colombo 03", "Colombo 05", "Colombo 07", "Battaramulla",
    "Malabe", "Kandy", "Galle", "Negombo", "Kurunegala", "Matara",
    "Jaffna", "Gampaha", "Nugegoda", "Dehiwala", "Ratnapura",
    "Anuradhapura", "Badulla", "Panadura", "Kelaniya", "Homagama",
]


COMPANIES = {
    "tech": [
        "IFS R&D International", "Virtusa Pega", "WSO2", "99x",
        "Dialog Axiata PLC", "SLT Mobitel", "hSenid Software",
        "Pearson Lanka", "Sysco Labs", "Zone24x7", "Rootcode",
        "Eyepax IT Consulting", "Codelabs", "Innoserve Group",
    ],
    "corporate": [
        "John Keells Holdings", "Hayleys PLC", "Cargills Ceylon PLC",
        "Aitken Spence", "Hemas Holdings", "Melstacorp",
        "Sunshine Consumer Workforce", "Ceylon Biscuits Limited",
        "Brandix Lanka", "MAS Holdings", "Hirdaramani Group",
        "Commercial Bank of Ceylon", "Sampath Bank", "Hatton National Bank",
        "People's Bank", "Bank of Ceylon", "NDB Bank", "DFCC Bank",
        "Ceylinco Insurance", "Union Assurance", "Softlogic Holdings",
        "Abans PLC", "Softwave Printing Solutions",
    ],
    "public": [
        "Ministry of Health", "Department of Education",
        "Ceylon Electricity Board", "National Water Supply Board",
        "Sri Lanka Railways", "Urban Development Authority",
        "Board of Investment of Sri Lanka", "Sri Lanka Customs",
    ],
}


UNIVERSITIES = [
    "University of Moratuwa", "University of Colombo",
    "University of Peradeniya", "University of Sri Jayewardenepura",
    "University of Kelaniya", "University of Ruhuna",
    "University of Jaffna", "Rajarata University",
    "SLIIT (Sri Lanka Institute of Information Technology)",
    "NSBM Green University", "NIBM (National Institute of Business Management)",
    "Sri Lanka Institute of Tourism & Hotel Management",
    "Aquinas College of Higher Studies", "ICBT Campus",
    "ESOFT Metro Campus", "Lanka Institute of Advanced Technology",
]


DEGREES = [
    "BSc (Hons) in {field}", "Bachelor of Science in {field}",
    "BA (Hons) in {field}", "Higher National Diploma in {field} (NVQ L6)",
    "Diploma in {field}", "MSc in {field}",
]


LANGUAGES = [
    "Sinhala (native), Tamil (fluent), English (professional)",
    "Sinhala (native), English (fluent)",
    "Tamil (native), Sinhala (fluent), English (professional)",
    "English (native proficiency), Sinhala (fluent)",
]


def phone():
    return "+94 " + random.choice(
        ["71", "77", "76", "70", "75", "78", "81"]
    ) + " " + str(random.randint(1000000, 9999999))


def years_block():
    end = random.randint(2024, 2026)
    span = random.randint(1, 6)
    return end - span, end


def pick_skills(pool, minimum=5):
    count = random.randint(minimum, min(len(pool), minimum + 4))
    return random.sample(pool, count)


# ------------------------------------------------------------------
# Category definitions: roles, skills, tasks, education fields,
# employer pool. Kept rich so combinations stay unique.
# ------------------------------------------------------------------

CATEGORIES = {
    "INFORMATION-TECHNOLOGY": {
        "roles": ["Software Engineer", "Associate Software Engineer", "DevOps Engineer", "QA Engineer", "Systems Analyst", "Data Engineer"],
        "skills": ["Python", "Java", "JavaScript", "SQL", "Git", "Docker", "REST API", "AWS", "React", "Linux", "CI/CD", "Unit Testing", "Agile", "MongoDB"],
        "tasks": ["developed RESTful microservices used by 50k+ users", "automated CI/CD pipelines cutting release time by 40%", "built responsive dashboards with React", "wrote unit and integration tests raising coverage to 85%", "optimized SQL queries reducing load time by half", "migrated legacy services to containerized workloads"],
        "fields": ["Information Technology", "Software Engineering", "Computer Science"],
        "pool": "tech",
    },
    "BUSINESS-DEVELOPMENT": {
        "roles": ["Business Development Executive", "Business Development Manager", "Key Account Executive", "Corporate Sales Officer", "Partnerships Lead"],
        "skills": ["Lead Generation", "Negotiation", "CRM", "Market Research", "Client Relations", "Sales Strategy", "Presentation Skills", "Microsoft Office", "Contract Management", "B2B Sales"],
        "tasks": ["grew the client portfolio by 30% year on year", "negotiated corporate agreements worth over LKR 25Mn annually", "identified new market segments across the Western Province", "maintained relationships with 40+ key accounts", "prepared weekly pipeline reports for senior management"],
        "fields": ["Business Management", "Marketing Management", "International Business"],
        "pool": "corporate",
    },
    "ACCOUNTANT": {
        "roles": ["Accountant", "Assistant Accountant", "Accounts Executive", "Senior Accountant", "Audit Associate"],
        "skills": ["Financial Reporting", "QuickBooks", "Sage Accpac", "Bank Reconciliation", "Taxation (IRD)", "Auditing", "Excel", "Accounts Payable", "Budgeting", "CA Sri Lanka knowledge"],
        "tasks": ["prepared monthly management accounts within deadlines", "handled VAT and SSCL filings to Inland Revenue", "reconciled 15+ bank accounts monthly", "supported annual statutory audits with zero major findings", "streamlined accounts payable reducing processing time by 25%"],
        "fields": ["Accounting", "Finance", "Commerce"],
        "pool": "corporate",
    },
    "FINANCE": {
        "roles": ["Financial Analyst", "Investment Analyst", "Treasury Officer", "Credit Analyst", "Fund Accountant"],
        "skills": ["Financial Modelling", "Valuation", "Excel", "Power BI", "Risk Analysis", "Portfolio Management", "Bloomberg basics", "IFRS", "Forecasting", "Capital Markets"],
        "tasks": ["built valuation models supporting LKR 400Mn investment decisions", "produced daily liquidity reports for treasury", "analysed credit exposure across 200+ counterparties", "forecasted cash flows improving planning accuracy by 18%"],
        "fields": ["Finance", "Financial Management", "Economics"],
        "pool": "corporate",
    },
    "BANKING": {
        "roles": ["Banking Assistant", "Customer Relationship Officer", "Credit Officer", "Branch Operations Executive", "Recoveries Officer"],
        "skills": ["Retail Banking", "Credit Appraisal", "KYC/AML Compliance", "Customer Service", "Core Banking Systems", "Loan Documentation", "Cash Handling", "Cross-selling", "Regulatory Compliance (CBSL)"],
        "tasks": ["processed housing and personal loan applications end to end", "achieved 120% of quarterly deposit mobilisation targets", "ensured KYC compliance across 500+ customer files", "resolved customer queries maintaining a 95% satisfaction score"],
        "fields": ["Banking and Finance", "Management", "Commerce"],
        "pool": "corporate",
    },
    "HEALTHCARE": {
        "roles": ["Medical Officer", "Nursing Officer", "Pharmacist", "Lab Technologist", "Healthcare Administrator"],
        "skills": ["Patient Care", "Clinical Documentation", "Phlebotomy", "Medical Terminology", "Infection Control", "Triage", "SLMC Registration", "Pharmacy Dispensing", "Laboratory Testing"],
        "tasks": ["managed an average of 60 outpatients per shift", "administered medication adhering to SLMC guidelines", "conducted laboratory investigations with 99% accuracy", "maintained sterile protocols in the surgical ward"],
        "fields": ["Medicine", "Nursing", "Pharmacy", "Medical Laboratory Science"],
        "pool": "public",
    },
    "HR": {
        "roles": ["HR Executive", "HR Generalist", "Talent Acquisition Specialist", "HR Coordinator", "Payroll Officer"],
        "skills": ["Recruitment", "Payroll Processing", "Employee Relations", "EPF/ETF Compliance", "Performance Management", "HRIS", "Onboarding", "Labour Law Basics", "Training Coordination"],
        "tasks": ["recruited 80+ candidates across tech and operations roles", "processed payroll for 600 employees with EPF/ETF compliance", "reduced average time-to-hire from 45 to 28 days", "rolled out a company-wide performance appraisal cycle"],
        "fields": ["Human Resource Management", "Business Management", "Psychology"],
        "pool": "corporate",
    },
    "SALES": {
        "roles": ["Sales Executive", "Area Sales Manager", "Territory Sales Officer", "Retail Sales Supervisor", "Direct Sales Representative", "Digital Sales Executive"],
        "skills": ["Sales Target Management", "Negotiation", "Distribution Management", "FMCG Knowledge", "Merchandising", "Team Leadership", "Route Planning", "Customer Retention", "Reporting", "Digital Marketing", "SEO", "Google Ads", "Social Media Marketing"],
        "tasks": ["exceeded monthly sales targets by 15% consistently", "managed 30+ dealer networks in the Kurunegala district", "launched two product lines achieving island-wide distribution", "trained a team of 12 sales representatives", "ran paid social campaigns that lifted online orders by 45%"],
        "fields": ["Marketing", "Business Management", "Agriculture", "Marketing Management"],
        "pool": "corporate",
    },
    "ENGINEERING": {
        "roles": ["Mechanical Engineer", "Electrical Engineer", "Site Engineer", "Maintenance Engineer", "Production Engineer"],
        "skills": ["AutoCAD", "SolidWorks", "Project Management", "Preventive Maintenance", "Lean Manufacturing", "HVAC", "Electrical Wiring Regulations", "Quality Assurance", "Site Supervision", "MS Project"],
        "tasks": ["supervised installation of a 500 kVA backup power system", "reduced machine downtime by 22% via preventive maintenance scheduling", "led a factory floor layout redesign under lean principles", "coordinated contractors for a LKR 80Mn construction phase"],
        "fields": ["Mechanical Engineering", "Electrical Engineering", "Civil Engineering"],
        "pool": "corporate",
    },
    "CONSTRUCTION": {
        "roles": ["Construction Site Supervisor", "Quantity Surveyor", "Civil Foreman", "Project Coordinator", "Building Inspector"],
        "skills": ["Quantity Surveying", "BOQ Preparation", "AutoCAD", "Site Safety (OSHA)", "Concrete Technology", "Surveying Instruments", "Cost Estimation", "Contract Administration"],
        "tasks": ["supervised high-rise concrete works up to the 12th floor", "prepared BOQs valuing over LKR 300Mn", "enforced site safety with zero lost-time incidents", "measured and certified contractor interim payments"],
        "fields": ["Construction Management", "Civil Engineering", "Quantity Surveying"],
        "pool": "corporate",
    },
    "TEACHER": {
        "roles": ["English Teacher", "Mathematics Teacher", "Science Teacher", "Primary School Teacher", "ICT Teacher"],
        "skills": ["Lesson Planning", "Classroom Management", "Curriculum Development", "Student Assessment", "Google Classroom", "Differentiated Instruction", "Parent Communication"],
        "tasks": ["taught mathematics to grades 6-11 following the national curriculum", "raised average exam pass rates by 14 percentage points", "organised inter-school science exhibitions", "introduced digital learning tools across 8 classrooms"],
        "fields": ["Education", "English Literature", "Mathematics", "Science Education"],
        "pool": "public",
    },
    "DESIGNER": {
        "roles": ["Graphic Designer", "UI/UX Designer", "Creative Designer", "Multimedia Designer", "Packaging Designer"],
        "skills": ["Adobe Photoshop", "Adobe Illustrator", "Figma", "Typography", "Branding", "Wireframing", "Motion Graphics", "Print Production", "Prototyping"],
        "tasks": ["designed brand identities for 20+ local SMEs", "created UI flows for a fintech mobile app with 100k downloads", "delivered print-ready packaging for FMCG clients", "built a reusable design system cutting production time by 30%"],
        "fields": ["Graphic Design", "Visual Communication", "Multimedia"],
        "pool": "corporate",
    },
    "CHEF": {
        "roles": ["Chef de Partie", "Sous Chef", "Commis Chef", "Head Chef", "Pastry Chef"],
        "skills": ["Food Preparation", "HACCP", "Menu Engineering", "Kitchen Supervision", "Cost Control", "Sri Lankan Cuisine", "Continental Cuisine", "Food Safety Standards", "Inventory Management"],
        "tasks": ["managed the à la carte section serving 200+ covers nightly", "designed seasonal menus reducing food cost by 9%", "enforced HACCP standards passing all health audits", "trained junior commis chefs on classical techniques"],
        "fields": ["Culinary Arts", "Hospitality Management"],
        "pool": "corporate",
    },
    "AVIATION": {
        "roles": ["Ground Handling Agent", "Cabin Crew", "Airport Operations Officer", "Cargo Operations Executive", "Passenger Service Agent"],
        "skills": ["Passenger Handling", "Load Control", "IATA Regulations", "Reservation Systems", "Safety Procedures", "Baggage Handling", "Customer Service", "Ramp Operations"],
        "tasks": ["coordinated turnaround for 8 daily international flights", "assisted passengers ensuring smooth check-in during peak season", "monitored ramp safety compliant with IATA AHM", "processed cargo documentation for export consignments"],
        "fields": ["Aviation Management", "Travel and Tourism Management"],
        "pool": "corporate",
    },
    "AGRICULTURE": {
        "roles": ["Agriculture Officer", "Plantation Manager", "Agronomist", "Livestock Development Officer", "Agri-business Executive"],
        "skills": ["Crop Management", "Soil Analysis", "Pest Control", "Irrigation Systems", "Dairy Management", "Agri-input Sales", "Extension Services", "Greenhouse Cultivation"],
        "tasks": ["advised 150+ farmer families on paddy cultivation practices", "increased tea smallholding yields by 18% through better plucking rounds", "managed a 40-acre coconut estate's fertiliser programme", "conducted soil tests and recommended correction plans"],
        "fields": ["Agricultural Technology", "Agriculture", "Animal Science"],
        "pool": "public",
    },
    "APPAREL": {
        "roles": ["Apparel Merchandiser", "Production Executive", "Quality Assurance Executive", "Pattern Maker", "Compliance Officer"],
        "skills": ["Merchandising", "Garment Technology", "Production Planning", "Quality Control (AQL)", "Buyer Communication", "Line Balancing", "Costing", "Ethical Compliance"],
        "tasks": ["handled UK buyer accounts worth USD 3Mn annually", "coordinated sampling to bulk production for 60+ styles per season", "maintained AQL 2.5 quality levels across lines", "ensured WRAP compliance during buyer audits"],
        "fields": ["Fashion Design", "Apparel Production", "Textile Technology"],
        "pool": "corporate",
    },
    "BPO": {
        "roles": ["Customer Service Representative", "Team Leader - BPO", "Technical Support Associate", "Voice Process Executive", "Chat Support Agent"],
        "skills": ["Customer Service", "Call Handling", "CRM Software", "Typing Speed 40+wpm", "Problem Solving", "Communication Skills", "Shift Flexibility", "UK/US Accent Neutralisation"],
        "tasks": ["handled 80+ inbound calls daily meeting CSAT targets", "resolved broadband technical tickets for an ISP client", "mentored new agents improving team CSAT by 8 points", "maintained 98% adherence to rota schedules"],
        "fields": ["Business Management", "Information Technology", "English"],
        "pool": "corporate",
    },
    "PUBLIC-RELATIONS": {
        "roles": ["PR Executive", "Communications Officer", "Corporate Communications Executive", "Event Coordinator", "Media Relations Officer"],
        "skills": ["Press Release Writing", "Media Liaison", "Event Management", "Social Media Management", "Crisis Communication", "Copywriting", "Stakeholder Engagement"],
        "tasks": ["secured coverage in leading national dailies for 10+ campaigns", "organised press conferences attended by 40+ journalists", "drafted executive speeches and corporate newsletters", "managed social media responses during a product recall"],
        "fields": ["Mass Communication", "Journalism", "Public Relations"],
        "pool": "corporate",
    },
    "DIGITAL-MEDIA": {
        "roles": ["Content Creator", "Video Editor", "Social Media Executive", "Digital Media Producer", "Podcast Producer"],
        "skills": ["Adobe Premiere Pro", "After Effects", "Canva", "YouTube SEO", "Content Strategy", "Photography", "Storyboarding", "Analytics", "Live Streaming"],
        "tasks": ["produced 100+ short-form videos totalling 5Mn views", "edited corporate documentaries for bank clients", "grew a YouTube channel from 0 to 50k subscribers", "livestreamed national-level esports events"],
        "fields": ["Mass Communication", "Digital Media", "Film and Television"],
        "pool": "corporate",
    },
    "ADVOCATE": {
        "roles": ["Attorney-at-Law", "Legal Officer", "Junior Counsel", "Company Secretary Assistant", "Conveyancing Clerk"],
        "skills": ["Litigation", "Legal Drafting", "Conveyancing", "Company Law", "Labour Disputes", "Notarial Work", "Legal Research", "Court Procedure"],
        "tasks": ["represented clients in District Court civil matters", "drafted deeds and notarial documents independently", "advised corporates on Employment Act compliance", "prepared briefs for counsel in commercial disputes"],
        "fields": ["Law", "Commercial Law"],
        "pool": "corporate",
    },
    "ARTS": {
        "roles": ["Creative Writer", "Art Director", "Performing Artist", "Photographer", "Content Writer"],
        "skills": ["Creative Writing", "Storytelling", "Adobe Creative Suite", "Stage Performance", "Sinhala Copywriting", "Poetry", "Art Curation", "Translation"],
        "tasks": ["published short stories in national weekend papers", "curated three group exhibitions at local galleries", "translated marketing copy between Sinhala and English", "scripted a radio drama series of 20 episodes"],
        "fields": ["Fine Arts", "Sinhala", "English Literature", "Performing Arts"],
        "pool": "corporate",
    },
    "FITNESS": {
        "roles": ["Fitness Instructor", "Personal Trainer", "Gym Manager", "Yoga Instructor", "Strength Coach"],
        "skills": ["Personal Training", "Nutrition Planning", "Group Fitness", "First Aid Certified", "Body Composition Analysis", "Strength Programming", "Client Motivation"],
        "tasks": ["trained 40+ regular clients with personalised programmes", "led morning group classes with 25 average attendance", "helped clients achieve documented weight-loss milestones", "maintained gym equipment safety checks"],
        "fields": ["Sports Science", "Physical Education", "Fitness Training"],
        "pool": "corporate",
    },
    "CONSULTANT": {
        "roles": ["Business Analyst", "Management Consultant", "Process Improvement Consultant", "ISO Consultant", "Strategy Associate"],
        "skills": ["Business Analysis", "Process Mapping", "ISO 9001", "Gap Assessment", "Report Writing", "Stakeholder Workshops", "Excel", "Slide Deck Creation", "Requirements Gathering"],
        "tasks": ["mapped and re-engineered order-to-cash processes for an apparel exporter", "guided 12 SMEs to ISO certification readiness", "facilitated workshops with C-suite stakeholders", "quantified savings of LKR 15Mn from process improvements"],
        "fields": ["Business Analysis", "Management", "Project Management"],
        "pool": "corporate",
    },
    "AUTOMOBILE": {
        "roles": ["Automobile Engineer", "Automotive Technician", "Service Advisor", "Workshop Supervisor", "Vehicle Sales Executive"],
        "skills": ["Vehicle Diagnostics", "Engine Overhauling", "Hybrid Vehicle Systems", "Auto Electrical", "Suspension Systems", "Customer Handling", "Service Scheduling", "OBD Scanners"],
        "tasks": ["diagnosed and repaired hybrid drivetrain faults", "supervised a workshop team of 9 technicians", "managed service bookings improving bay utilisation by 20%", "carried out pre-delivery inspections for 30+ vehicles monthly"],
        "fields": ["Automobile Engineering", "Motor Vehicle Technology"],
        "pool": "corporate",
    },
}


def build_resume(category_name, spec):
    """Compose one synthetic resume text."""

    name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"

    city = random.choice(CITIES)

    role = random.choice(spec["roles"])

    skills = pick_skills(spec["skills"])

    start_year, end_year = years_block()

    company = random.choice(COMPANIES[spec["pool"]])

    degree_field = random.choice(spec["fields"])

    degree = random.choice(DEGREES).format(field=degree_field)

    university = random.choice(UNIVERSITIES)

    grad_year = start_year - random.randint(0, 3)

    tasks = random.sample(spec["tasks"], k=min(4, len(spec["tasks"])))

    languages = random.choice(LANGUAGES)

    sections = []

    # Header
    sections.append(f"{name}")
    sections.append(f"{role}")
    sections.append(
        f"{city}, Sri Lanka | {phone()} | "
        f"{name.split()[0].lower()}{random.randint(10, 99)}"
        f"@gmail.com | linkedin.com/in/{name.lower().replace(' ', '-')}"
    )

    # Professional summary
    summary = (
        f"{role} based in {city} with {end_year - start_year}+ years of "
        f"experience in {category_name.replace('-', ' ').title().lower()} related roles. "
        f"Skilled in {', '.join(skills[:3])}. Known for delivering reliable "
        f"results, working well in teams and continuously improving processes. "
        f"Fluent in {languages.split('(')[0].strip().split(',')[0]} and English."
    )
    sections.append(f"Professional Summary\n{summary}")

    # Core skills
    sections.append(
        "Skills\n" + "\n".join(f"- {skill}" for skill in skills)
    )

    # Experience
    experience_lines = [
        f"{role} — {company}, {city}",
        f"{start_year} - {'Present' if random.random() < 0.4 else end_year}",
    ]
    experience_lines.extend(
        f"- Capitalised on task: {task}" if False else f"- {task[0].upper()}{task[1:]}"
        for task in tasks
    )
    sections.append("Work Experience\n" + "\n".join(experience_lines))

    # Previous shorter stint (adds variety + multi-company realism)
    if random.random() < 0.65:

        prev_company = random.choice(COMPANIES[spec["pool"]])

        while prev_company == company:
            prev_company = random.choice(COMPANIES[spec["pool"]])

        prev_start = start_year - random.randint(1, 3)

        prev_task = random.choice(spec["tasks"])

        sections.append(
            "Previous Experience\n"
            f"Trainee {role} — {prev_company}\n"
            f"{prev_start} - {start_year}\n"
            f"- {prev_task[0].upper()}{prev_task[1:]}"
        )

    # Education
    education = (
        f"Education\n{degree}, {university} ({grad_year})\n"
        f"G.C.E. Advanced Level examination — "
        f"{random.choice(['Maths', 'Commerce', 'Arts', 'Science', 'Technology'])} stream"
    )
    sections.append(education)

    # Certifications sometimes
    if random.random() < 0.5:
        cert = random.choice([
            "Certificate in Professional English — British Council Colombo",
            "Diploma in Computer Applications — NIBM",
            f"Professional certificate in {degree_field} — ICBT Campus",
            "NVQ Level 4 qualification",
        ])
        sections.append(f"Certifications\n{cert}")

    # Languages
    sections.append(f"Languages\n{languages}")

    return "\n\n".join(sections)


def normalize_for_dedup(text):
    """Lowercase alphanumerics only — catches trivial rewordings."""

    return re.sub(r"[^a-z0-9]", "", text.lower())


def main():
    rows = []
    seen_hashes = set()

    stats = {"generated": 0, "exact_dupes": 0, "near_dupes": 0}

    for category_name, spec in CATEGORIES.items():

        made = 0

        attempts = 0

        target = PER_CATEGORY

        while made < target and attempts < target * 12:

            attempts += 1

            text = build_resume(category_name, spec)

            stats["generated"] += 1

            norm = normalize_for_dedup(text)

            exact_hash = hashlib.md5(norm.encode()).hexdigest()

            # Near-duplicate signature: category + role words + first skills
            sig_source = (
                category_name
                + "|"
                + "|".join(sorted(norm[:220]))
            )

            sig_hash = hashlib.md5(sig_source.encode()).hexdigest()

            if exact_hash in seen_hashes:
                stats["exact_dupes"] += 1
                continue

            if sig_hash in seen_hashes:
                stats["near_dupes"] += 1
                continue

            seen_hashes.add(exact_hash)
            seen_hashes.add(sig_hash)

            rows.append({
                "ID": 90_000_000 + len(rows),
                "Resume_str": text,
                "Category": category_name,
            })

            made += 1

    df = pd.DataFrame(rows)

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    df.to_csv(OUTPUT_FILE, index=False)

    print(f"Generated : {stats['generated']}")
    print(f"Duplicates removed: exact={stats['exact_dupes']} near={stats['near_dupes']}")
    print(f"Saved     : {len(df)} resumes -> {OUTPUT_FILE}")
    print()
    print(df["Category"].value_counts().to_string())


if __name__ == "__main__":
    main()
