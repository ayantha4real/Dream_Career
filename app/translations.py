"""
Lightweight UI translations for DreamCareer.

Keys are the ENGLISH UI strings themselves — any string without
a translation automatically falls back to English, so partial
coverage is always safe.

Languages: English (en), Sinhala (si), Tamil (ta)
"""

LANGUAGES = {
    "en": "English",
    "si": "සිංහල",
    "ta": "தமிழ்",
}

TRANSLATIONS = {
    "si": {
        # Navigation
        "Home": "මුල් පිටුව",
        "Browse Jobs": "රැකියා බලන්න",
        "My History": "මගේ ඉතිහාසය",
        "Alerts": "දැනුම්දීම්",
        "Log in": "ඇතුල් වන්න",
        "Log out": "පිටවෙන්න",
        "Get started": "අරඹන්න",

        # Hero + upload
        "✦ Built for Sri Lankan job seekers": "✦ ශ්‍රී ලාංකික රැකියා සොයන්නන් සඳහා",
        "Find the career your resume is": "ඔබේ CV එකට වඩාත්ම ගැලපෙන වෘත්තිය",
        "built for.": "සොයා ගන්න.",
        "Upload your CV and instantly discover the careers that suit you, the skills you're missing, courses to learn them, and live jobs hiring right now — all in one report.": "ඔබේ CV උඩුගත කර ඔබට ගැලපෙන වෘත්තීන්, ඔබ සතුව නොමැති කුසලතා, ඒවා ඉගෙනීමට පාඨමාලා සහ දැන් බඳවා ගන්නා රැකියා එකවර සොයාගන්න.",
        "Analyze my CV": "මගේ CV විශ්ලේෂණය කරන්න",
        "Browse jobs": "රැකියා බලන්න",
        "Career fields": "වෘත්ති ක්ෂේත්‍ර",
        "Skills detected": "හඳුනාගත් කුසලතා",
        "Latest jobs": "නවතම රැකියා",
        "📄 Analyze your resume": "📄 ඔබේ CV විශ්ලේෂණය කරන්න",
        "Click to upload or drag & drop": "ක්ලික් කර උඩුගත කරන්න හෝ ඇද දමන්න",
        "🚀 Analyze My Career": "🚀 මගේ වෘත්තිය විශ්ලේෂණය කරන්න",

        # Steps guide
        "How it works": "ක්‍රියා කරන ආකාරය",
        "Three simple steps to your next job": "ඔබේ ඊළඟ රැකියාවට පියවර තුනක්",
        "Upload your CV": "ඔබේ CV උඩුගත කරන්න",
        "Drop in your PDF resume — it only takes a few seconds.": "ඔබේ PDF CV එක එකතු කරන්න — තත්පර කිහිපයක් පමණි.",
        "See your best-fit careers": "ඔබට ගැලපෙන වෘත්තීන් බලන්න",
        "We compare your skills with real career paths and show exactly where you stand.": "ඔබේ කුසලතා සැබෑ වෘත්ති මාර්ග සමඟ සංසන්දනය කර ඔබේ තත්ත්වය පැහැදිලිව පෙන්වයි.",
        "Learn & apply": "ඉගෙනීම සහ අයදුම් කිරීම",
        "Get course suggestions for missing skills and apply to live jobs that match.": "අසම්පූර්ණ කුසලතා සඳහා පාඨමාලා යෝජනා ලබා ගෙන ගැලපෙන රැකියාවලට අයදුම් කරන්න.",

        # Radar & jobs
        "Market intelligence": "රැකියා වෙළඳපොළ නැඹුරු",
        "📡 Skill Demand Radar": "📡 කුසලතා ඉල්ලුම් දර්ශකය",
        "Compare with my skills →": "මගේ කුසලතා සමඟ සසඳන්න →",
        "Latest opportunities": "නවතම අවස්ථා",
        "View all →": "සියල්ල බලන්න →",
        "View all": "සියල්ල බලන්න",
        "Live listings": "සජීවී නිවේදන",
        "Job board": "රැකියා පුවරුව",
        "Search": "සොයන්න",
        "Clear": "මකන්න",
        "All fields": "සියලු ක්ෂේත්‍ර",
        "No matching jobs": "ගැලපෙන රැකියා නොමැත",
        "Details": "විස්තර",
        "Company not specified": "සමාගම සඳහන් නොකර ඇත",

        # Auth
        "Welcome back": "සාදරයෙන් පිළිගනිමු",
        "Username or email": "පරිශීලක නාමය හෝ ඊමේල්",
        "Password": "මුරපදය",
        "Create a free account": "නොමිලේ ගිණුමක් සාදන්න",
        "Create your account": "ඔබේ ගිණුම සාදන්න",
        "Username": "පරිශීලක නාමය",
        "Email": "ඊමේල්",
        "Confirm": "තහවුරු කරන්න",
        "Log in": "ඇතුල් වන්න",
        "Log out": "පිටවෙන්න",
        "Get started": "අරඹන්න",

        # Buttons / common
        "Analyze My Career": "🚀 මගේ වෘත්තිය විශ්ලේෂණය කරන්න",
        "Upload your CV": "ඔබේ CV උඩුගත කරන්න",
        "Analyze my CV": "මගේ CV විශ්ලේෂණය කරන්න",
        "Analyze my resume": "මගේ CV විශ්ලේෂණය කරන්න",

        # Results page headings
        "Careers that suit you most": "ඔබට ගැලපෙන වෘත්තීන්",
        "What influenced your match": "ඔබේ ගැලපීමට බලපා සිදුවූ දේවල්",
        "Skills we found in your resume": "ඔබේ CV තුළ හඳුනාගත් කුසලතා",
        "More about your resume": "ඔබේ CV ගැන වැඩියෙන්",
        "Skill-based career recommendations": "කුසලතා පදනම් වෘත්ති නිර්දේශ",
        "Recommended live jobs": "නිර්දේශිත සජීව රැකියා",
        "Download / Print report (PDF)": "වාර්තාව බාගත / මුද්‍රණය (PDF)",
        "Analyze another resume": "වෙනත් CV විශ්ලේෂණය කරන්න",
        "Your fit for": "ඔබේ ගැලපීම",
        "You have": "ඔබට ඇතියි",
        "This posting also asks for": "මෙම දැනුම්දීමේ ද ඉල්ලා සිටියි",
        "Ready to apply": "අයදුම් කිරීමට සූදානම්",
        "Almost there": "ඉතා අතට ගියා",
        "Stretch role": "අධික පුරුදු රැකියාවක්",
        "Match your skills": "ඔබේ කුසලතා සමඟ සමාන කරන්න",
    },
    "ta": {
        # Navigation
        "Home": "முகப்பு",
        "Browse Jobs": "வேலைவாய்ப்புகள்",
        "My History": "எனது வரலாறு",
        "Alerts": "எச்சரிக்கைகள்",
        "Log in": "உள்நுழைக",
        "Log out": "வெளியேறு",
        "Get started": "தொடங்குங்கள்",

# Hero + upload
    "✦ Built for Sri Lankan job seekers": "✦ இலங்கை வேலை தேடுபவர்களுக்காக",
    "Find the career your resume is": "உங்கள் CV-க்கு மிகவும் பொருத்தமான தொழிலை",
    "built for.": "கண்டறியுங்கள்.",
    "Upload your CV and instantly discover the careers that suit you, the skills you're missing, courses to learn them, and live jobs hiring right now — all in one report.": "உங்கள் CV-ஐ பதிவேற்றி, உங்களுக்கு பொருத்தமான தொழில்கள், உங்களிடம் விலங்கான திறமைகள், அவற்றை கற்கும் பாடநெறிகள், மற்றும் இப்போதே வேலைவாய்ப்புகளை ஒரு அறிக்கையில் அறியுங்கள்.",
    "Analyze my CV": "எனது CV-ஐ பகுப்பாய்வு செய்யுங்கள்",
    "Browse jobs": "வேலைவாய்ப்புகள்",
    "Career fields": "தொழில் துறைகள்",
    "Skills detected": "கண்டறிந்த திறமைகள்",
    "Latest jobs": "சமீபத்திய வேலைகள்",
    "📄 Analyze your resume": "📄 உங்கள் CV-ஐ பகுப்பாய்வு செய்யுங்கள்",
    "Click to upload or drag & drop": "கிளிக் செய்து பதிவேற்றவும் அல்லது இழுத்து இடுங்கள்",
    "🚀 Analyze My Career": "🚀 எனது தொழிலை பகுப்பாய்வு செய்யுங்கள்",

        # Steps guide
        "How it works": "எப்படி வேலை செய்கிறது",
        "Three simple steps to your next job": "உங்கள் அடுத்த வேலைக்கு மூன்று எளிய படிகள்",
        "Upload your CV": "உங்கள் CV-ஐ பதிவேற்றுங்கள்",
        "Drop in your PDF resume — it only takes a few seconds.": "உங்கள் PDF CV-ஐ சேர்க்கவும் — சில வினாடிகள் மட்டுமே.",
        "See your best-fit careers": "உங்களுக்கு ஏற்ற தொழில்களைப் பாருங்கள்",
        "We compare your skills with real career paths and show exactly where you stand.": "உங்கள் திறமைகளை உண்மையான தொழில் பாதைகளுடன் ஒப்பிட்டு உங்கள் நிலையைக் காட்டுகிறோம்.",
        "Learn & apply": "கற்றுக்கொண்டு விண்ணப்பிக்கவும்",
        "Get course suggestions for missing skills and apply to live jobs that match.": "காணாமல் போன திறமைகளுக்கான பாடநெறி பரிந்துரைகளைப் பெற்று, பொருத்தமான வேலைகளுக்கு விண்ணப்பிக்கவும்.",

        # Radar & jobs
        "Market intelligence": "சந்தை நாடாங்கள்",
        "📡 Skill Demand Radar": "📡 திறமை தேவை ரேடார்",
        "Compare with my skills →": "எனது திறமைகளுடன் ஒப்பிடுங்கள் →",
        "Latest opportunities": "சமீபத்திய வாய்ப்புகள்",
        "View all →": "அனைத்தையும் பார்க்கவும் →",
        "View all": "அனைத்தையும் பார்க்கவும்",
        "Live listings": "நேரடி அறிவிப்புகள்",
        "Job board": "வேலை பலகை",
        "Search": "தேடு",
        "Clear": "அழி",
        "All fields": "அனைத்து துறைகள்",
        "No matching jobs": "பொருத்தமான வேலைகள் இல்லை",
        "Details": "விவரங்கள்",
        "Company not specified": "நிறுவனம் குறிப்பிடப்படவில்லை",

        # Auth
        "Welcome back": "மீண்டும் வருக",
        "Username or email": "பயனர் பெயர் அல்லது மின்னஞ்சல்",
        "Password": "கடவுச்சொல்",
        "Create a free account": "இலவச கணக்கை உருவாக்குங்கள்",
        "Create your account": "உங்கள் கணக்கை உருவாக்குங்கள்",
        "Username": "பயனர் பெயர்",
        "Email": "மின்னஞ்சல்",
        "Confirm": "உறுதிப்படுத்து",
        "Log in": "உள்நுழைக",
        "Log out": "வெளியேறு",
        "Get started": "தொடங்குங்கள்",

        # Buttons / common
        "Analyze My Career": "🚀 எனது தொழிலை பகுப்பாய்வு செய்யுங்கள்",
        "Upload your CV": "உங்கள் CV-ஐ பதிவேற்றுங்கள்",
        "Analyze my CV": "எனது CV-ஐ பகுப்பாய்வு செய்யுங்கள்",
        "Analyze my resume": "எனது CV-ஐ பகுப்பாய்வு செய்யுங்கள்",

        # Results page headings
        "Careers that suit you most": "உங்களுக்கு ஏற்ற தொழில்கள்",
        "What influenced your match": "உங்கள் பொருத்தத்தைத் தாக்கிய அம்சங்கள்",
        "Skills we found in your resume": "உங்கள் CV-இல் கண்டறிந்த திறமைகள்",
        "More about your resume": "உங்கள் CV-உடன் தொடர்புடைய மேலும் விவரங்கள்",
        "Skill-based career recommendations": "திறமை அடிப்படையில் தொழில் பரிந்துரைகள்",
        "Recommended live jobs": "பரிந்துரை செய்யப்பட்ட நேரடி வேலைகள்",
        "Download / Print report (PDF)": "அறிக்கையை பதிவிறக்க / அச்சிடு (PDF)",
        "Analyze another resume": "மற்ற CV-ஐ பகுப்பாய்வு செய்யுங்கள்",
        "Your fit for": "உங்களுக்கான பொருத்தம்",
        "You have": "உங்களிடம் உள்ளது",
        "This posting also asks for": "இந்த அறிவிப்பும் இதை எதிர்பார்க்கிறது",
        "Ready to apply": "விண்ணப்பிக்க முப்பெறும் நிலை",
        "Almost there": "அत्यന്ത அருகில்",
        "Stretch role": "விரிவான விருப்பங்கள் தேவைப்படும் வேலை",
        "Match your skills": "உங்கள் திறமைகளுடன் பொருத்தவும்",
    },
}