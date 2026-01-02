"""Hierarchical document classification system - Domain → Category → FileType"""

import logging
from typing import Dict

logger = logging.getLogger(__name__)


class DocumentClassifier:
    """Handles hierarchical document classification with scaled keyword system"""
    
    # Domain-level keywords (Expanded for V5/V6)
    DOMAIN_KEYWORDS = {
        "Technology": {
            "strong": ["uav", "drone", "robot", "robotics", "unmanned", "quadcopter", "hexacopter", "flight",
                      "web application", "website", "web development", "web design",
                      "cloud computing", "cloud infrastructure", "devops", "docker", "kubernetes", 
                      "aws", "azure", "gcp", "cloud platform", "serverless",
                      "database architecture", "data warehouse", "nosql", "mongodb", "postgres", "mysql", "redis", "elasticsearch",
                      "api architecture", "rest api", "api design", "api development",
                      "infrastructure", "infrastructure as code", "terraform", "ansible",
                      "ssl", "tls", "ssl certificate", "tls certificate", "encryption", "authentication protocol", "authorization",
                      "cipher", "cryptography", "symmetric", "asymmetric", "decryption", "hashing", "aes", "rsa", "sha",
                      "git workflow", "version control system", "ci/cd pipeline", "jenkins", "gitlab ci", "github actions",
                      "iot", "iot device", "sensor", "edge computing", "embedded system",
                      "network", "networking", "firewall", "proxy", "load balancer",
                      "deployment", "containerization", "microservice architecture"],
            "weak": ["tech", "technology", "system", "platform", "solution", "tool", "hardware"]
        },
        "Code": {
            "strong": ["backend development", "backend code", "backend service", "api development",
                      "api endpoint", "rest api", "rest architecture", "graphql", "grpc",
                      "nodejs", "express", "django", "flask", "fastapi", "spring", "java",
                      "react", "vue", "angular", "frontend development", "frontend code",
                      "jsx", "tsx", "html", "css", "javascript", "typescript",
                      "algorithm", "data structure", "sorting", "searching", "recursion",
                      "unit test", "integration test", "testing", "test case",
                      "database", "sql", "nosql", "orm", "query", "schema",
                      "function", "method", "class", "object", "async", "await",
                      "authentication", "authorization", "middleware", "error handling",
                      "array", "list", "dictionary", "set", "tuple", "hash",
                      "tree", "graph", "binary", "traversal", "bfs", "dfs",
                      "refactor", "optimize", "debug", "logging", "cache",
                      "time complexity", "space complexity", "big o", "dynamic programming",
                      "inheritance", "polymorphism", "encapsulation", "abstraction",
                      "decorator", "closure", "lambda", "functional programming",
                      "swagger", "openapi", "documentation", "code review", "test driven"],
            "weak": ["code", "programming", "script", "logic", "development", "source"]
        },
        "Finance": {
            "strong": ["revenue", "profit", "loss", "cost", "budget", "budgeting", "forecast", "forecasting",
                      "investment", "roi", "return on investment", "financial", "accounting", "bookkeeping",
                      "balance sheet", "income statement", "cash flow", "statement of cash flows", "fiscal",
                      "audit", "auditor", "auditing", "stock", "equity", "dividend", "dividend yield",
                      "payroll", "salary", "wage", "compensation", "benefits", "deduction", "withholding",
                      "expense", "expense report", "reimbursement", "invoice", "receipt",
                      "tax", "taxation", "tax return", "irs", "deduction", "filing", "deadline",
                      "depreciation", "amortization", "asset", "liability", "net worth", "equity",
                      "capital", "capital expenditure", "operating expense", "opex", "capex",
                      "maintenance", "maintenance cost", "repair", "repair cost", "upkeep",
                      "accounting standard", "gaap", "ifrs", "fasb", "sec", "sarbanes oxley",
                      "quarterly", "annual", "fiscal year", "reporting period", "financial statement"],
            "weak": ["money", "business", "financial", "payment", "transaction", "account", "ledger"]
        },
        "Education": {
            "strong": ["course", "curriculum", "lesson", "module", "unit", "chapter", "section",
                      "assignment", "homework", "worksheet", "exercise", "problem", "question",
                      "quiz", "exam", "test", "assessment", "evaluation", "grading", "grade",
                      "solution", "answer", "explanation", "tutorial", "guide", "handbook",
                      "learning objective", "learning outcome", "prerequisite", "syllabus",
                      "lecture", "classroom", "seminar", "workshop", "lab", "laboratory",
                      "teaching", "instruction", "pedagogy", "didactic", "educational", "academic",
                      "student", "learner", "pupil", "scholar", "teacher", "instructor", "professor",
                      "school", "university", "college", "academy", "institute", "institution",
                      "semester", "quarter", "year", "academic year", "school year", "term",
                      "grade level", "elementary", "middle school", "high school", "secondary",
                      "python course", "programming course", "math course", "science course",
                      "numpy", "pandas", "matplotlib", "seaborn", "plotly", "sklearn", "scikit-learn",
                      "tensorflow", "keras", "pytorch", "torch", "deep learning", "machine learning",
                      "neural network", "cnn", "rnn", "lstm", "transformer", "model", "training",
                      "dataset", "data", "analysis", "statistics", "statistical", "probability",
                      "supervised learning", "unsupervised learning", "reinforcement learning",
                      "classification", "regression", "clustering", "dimensionality reduction",
                      "feature engineering", "feature selection", "preprocessing", "normalization",
                      "training", "testing", "validation", "train test split", "cross validation",
                      "accuracy", "precision", "recall", "f1 score", "roc", "auc", "confusion matrix",
                      "optimization", "gradient descent", "backpropagation", "loss function",
                      "hyperparameter", "tuning", "grid search", "random search", "bayesian optimization"],
            "weak": ["educational", "study", "learn", "learning", "knowledge", "skill", "training"]
        },
        "College": {
            "strong": ["university", "college", "campus", "dormitory", "dorm", "residence hall",
                      "tuition", "fee", "scholarship", "grant", "financial aid", "loan", "student loan",
                      "degree", "bachelor", "master", "phd", "doctorate", "major", "minor", "specialization",
                      "gpa", "grade point average", "transcript", "diploma", "convocation",
                      "alumni", "alumnus", "alumna", "graduate", "commencement", "graduation",
                      "fraternity", "sorority", "greek life", "greek organization", "pledge",
                      "club", "organization", "student organization", "student group",
                      "student government", "senate", "council", "board", "president",
                      "registration", "course registration", "add drop", "course schedule",
                      "professor", "instructor", "faculty", "staff", "administrator", "dean",
                      "campus life", "student life", "residential life", "internship", "placement", "recruiting"],
            "weak": ["college", "university", "student", "campus", "academic"]
        },
        "School": {
            "strong": ["elementary", "elementary school", "middle school", "high school", "secondary",
                      "k-12", "k12", "public school", "private school", "charter school",
                      "grade", "grade level", "grade 1", "grade 10", "grade 12",
                      "classroom", "class", "period", "lunch period", "recess",
                      "teacher", "principal", "staff", "counselor", "nurse", "aide", "administrator",
                      "report card", "progress report", "behavior", "discipline", "detention",
                      "assignment", "homework", "worksheet", "project", "presentation", "poster",
                      "exam", "test", "quiz", "mid-term", "final exam", "board exam",
                      "schedule", "timetable", "class schedule", "bell schedule", "calendar",
                      "parent", "guardian", "parent teacher conference", "ptc", "pta", "pto",
                      "activity", "club", "sports", "athletics", "team", "game", "tournament",
                      "field trip", "assembly", "pep rally", "graduation", "commencement",
                      "bonafide certificate", "leaving certificate", "transfer certificate", "lc", "tc"],
            "weak": ["school", "education", "student", "learning", "teaching"]
        },
        "Company": {
            "strong": ["employee", "staff", "team", "department", "division", "unit",
                      "project", "initiative", "program", "campaign", "strategy",
                      "budget", "budgeting", "forecast", "planning", "deadline", "timeline",
                      "product", "product line", "product development", "roadmap", "feature",
                      "service", "service offering", "service delivery", "consulting",
                      "client", "customer", "vendor", "partner", "stakeholder", "supplier",
                      "human resources", "hr", "recruitment", "hiring", "onboarding", "offer letter",
                      "payroll", "compensation", "salary", "bonus", "incentive", "appraisal",
                      "meeting", "standup", "sync", "all hands", "town hall", "minutes of meeting", "mom",
                      "presentation", "pitch", "demo", "prototype", "mockup", "wireframe",
                      "quarterly", "q1", "q2", "q3", "q4", "fiscal quarter",
                      "annual", "annual report", "earnings", "revenue", "profit",
                      "performance", "kpi", "key performance indicator", "okr",
                      "review", "performance review", "feedback", "evaluation",
                      "office", "workspace", "remote", "hybrid", "wfh", "work from home",
                      "company culture", "values", "mission", "vision", "policy",
                      "business plan", "business model", "sales", "marketing",
                      "statement of work", "sow", "sla", "service level agreement",
                      "proposal", "contract", "nda", "non-disclosure"],
            "weak": ["company", "work", "business", "job", "employment", "professional"]
        },
        "Healthcare": {
            "strong": ["patient", "medical", "medicine", "physician", "doctor", "healthcare",
                      "hospital", "clinic", "medical center", "nursing home", "urgent care", "emergency", "icu",
                      "diagnosis", "diagnostic", "symptom", "treatment", "therapy", "clinical",
                      "prescription", "medication", "pharmaceutical", "drug", "vaccine",
                      "disease", "illness", "condition", "disorder", "syndrome",
                      "vital signs", "blood pressure", "heart rate", "temperature",
                      "surgery", "surgical", "operation", "anesthesia", "recovery",
                      "radiology", "x-ray", "ct scan", "mri", "ultrasound", "imaging",
                      "laboratory", "lab test", "blood test", "pathology", "biopsy",
                      "nursing", "nurse", "registered nurse", "discharge summary", "triage",
                      "opd", "outpatient", "inpatient", "admission", "medical history",
                      "insurance", "tpa", "claim", "cashless", "mediclaim",
                      "dicom", "hl7", "emr", "ehr", "medical record"],
            "weak": ["health", "medicine", "doctor", "medical", "care", "hospital"]
        },
        "Legal": {
            "strong": ["contract", "agreement", "lease agreement", "rent agreement",
                      "clause", "section", "article", "amendment", "addendum",
                      "party", "plaintiff", "defendant", "litigant", "attorney", "lawyer",
                      "law", "legal", "statute", "regulation", "act", "bill",
                      "copyright", "patent", "trademark", "intellectual property", "ip",
                      "liability", "indemnity", "insurance", "coverage",
                      "court", "lawsuit", "litigation", "legal action", "trial", "hearing",
                      "jurisdiction", "venue", "arbitration", "mediation",
                      "herein", "hereby", "whereas", "pursuant to", "in accordance with",
                      "effective date", "termination", "breach", "default",
                      "damages", "remedy", "injunction", "relief",
                      "warrant", "warranty", "represent", "covenant",
                      "affidavit", "power of attorney", "poa", "notary", "gazette"],
            "weak": ["legal", "law", "attorney", "rights", "rule"]
        },
        "Business": {
            "strong": ["strategy", "strategic plan", "business model", "value proposition",
                      "marketing", "marketing strategy", "advertising", "campaign",
                      "sales", "sales strategy", "sales pipeline", "funnel",
                      "customer", "customer experience", "crm", "customer retention",
                      "market", "market share", "market analysis", "competitive analysis",
                      "growth", "growth strategy", "expansion", "scaling",
                      "operations", "operational", "supply chain", "logistics",
                      "management", "leadership", "executive", "ceo", "cfo", "cto",
                      "organization", "organizational structure", "restructuring",
                      "planning", "objective", "goal", "milestone", "target",
                      "innovation", "disruption", "startup", "venture", "fundraising"],
            "weak": ["business", "company", "plan", "goal", "strategy", "market"]
        },
        "ResearchPaper": {
            "strong": ["abstract", "introduction", "methodology", "methods", "results", "discussion", "conclusion", "references",
                      "research", "study", "analysis", "experiment", "experimental",
                      "hypothesis", "hypothesis test", "statistical significance", "p-value",
                      "data", "data analysis", "qualitative", "quantitative",
                      "literature review", "related work", "citation", "cite", "bibliography",
                      "author", "researcher", "academic", "scholar", "affiliation",
                      "journal", "journal article", "peer review", "proceedings",
                      "conference", "symposium", "workshop",
                      "figure", "table", "graph", "chart", "diagram",
                      "et al", "doi", "isbn", "issn", "arxiv"],
            "weak": ["research", "paper", "academic", "study", "analysis", "thesis"]
        },
        "Documentation": {
            "strong": ["## ", "# ", "api", "api documentation", "endpoint",
                      "parameter", "parameters", "argument", "return value",
                      "response", "response code", "response body", "status code",
                      "schema", "json schema", "data model",
                      "authentication", "authorization", "oauth", "api key", "token",
                      "rest", "restful", "http method", "get", "post", "put", "delete",
                      "swagger", "openapi", "raml", "api blueprint",
                      "example", "usage example", "code snippet", "curl",
                      "guide", "getting started", "quick start", "installation", "setup",
                      "tutorial", "walkthrough", "step by step", "how to"],
            "weak": ["help", "explain", "guide", "reference", "doc", "manual"]
        },
        "Personal": {
            "strong": ["resume", "cv", "curriculum vitae", "biodata", "portfolio",
                      "utility bill", "electricity bill", "water bill", "gas bill",
                      "credit card statement", "bank statement", "passbook",
                      "rent agreement", "lease", "maintenance bill",
                      "receipt", "invoice", "warranty card", "guarantee",
                      "insurance policy", "premium receipt", "nomination",
                      "identity card", "id card", "visiting card",
                      "medical report", "prescription", "vaccination certificate"],
            "weak": ["personal", "home", "bill", "statement", "receipt"]
        },
        "Government": {
            "strong": ["aadhaar", "uidai", "pan card", "income tax", "it department",
                      "passport", "visa", "immigration",
                      "driving license", "dl", "vehicle registration", "rc",
                      "voter id", "election card", "epic",
                      "ration card", "domicile", "caste certificate",
                      "birth certificate", "death certificate", "marriage certificate",
                      "form 16", "itr", "income tax return", "acknowledgement",
                      "gazette", "notification", "circular", "gr", "government resolution",
                      "affidavit", "stamp paper", "notary"],
            "weak": ["government", "govt", "official", "certificate", "id"]
        }
    }
    
    def _guardrail_classify(self, text_lower: str, filename_lower: str, filename: str):
        """Apply explicit guardrail rules to prevent obvious misclassifications.
        Returns a forced classification dict or None.
        """
        ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''

        # Rules ordered by specificity and risk of misclassification
        rules = [
            # Government & Personal (High priority to catch IDs)
            {"domain":"Government","category":"ID","kw":["aadhaar", "pan card", "passport", "driving license", "voter id", "uidai"]},
            {"domain":"Government","category":"Tax","kw":["form 16", "itr-v", "income tax return", "computation of income"]},
            {"domain":"Personal","category":"Identity","kw":["curriculum vitae", "resume", "biodata"]},
            {"domain":"Personal","category":"Bills","kw":["electricity bill", "gas bill", "credit card statement"]},

            # Technology
            {"domain":"Technology","category":"UAV","kw":["uav","drone","quadcopter","aerial","hexacopter"]},
            {"domain":"Technology","category":"API","kw":["openapi","swagger","graphql","grpc","raml","api gateway","rest api","api documentation","http method"]},
            {"domain":"Technology","category":"DevOps","kw":["docker","kubernetes","k8s","jenkins","terraform","ansible","helm","github actions","gitlab ci","ci/cd"]},
            
            # Code (Frontend/Backend)
            {"domain":"Code","category":"Frontend","kw":["react","jsx","tsx","nextjs","<html","<!doctype","tailwind","redux","vue","angular"]},
            {"domain":"Code","category":"Backend","kw":["express","django","flask","fastapi","spring boot","server","middleware","controller"]},
            
            # Healthcare (Specific reports)
            {"domain":"Healthcare","category":"LabReport","kw":["pathology report", "blood test", "lipid profile", "cbc", "urine analysis"]},
            {"domain":"Healthcare","category":"Clinical","kw":["discharge summary", "opd paper", "prescription", "admission form"]},
            
            # School & College (Admin)
            {"domain":"School","category":"Admin","kw":["leaving certificate", "bonafide", "transfer certificate", "result sheet", "report card"]},
            {"domain":"College","category":"Admin","kw":["transcript", "degree certificate", "provisional certificate", "migration certificate"]},

            # Company (Product vs Service)
            {"domain":"Company","category":"Product","kw":["product requirements", "prd", "user story", "sprint backlog", "release notes"]},
            {"domain":"Company","category":"Service","kw":["statement of work", "sow", "service level agreement", "sla", "client proposal"]},
            
            # General Finance & Legal
            {"domain":"Finance","category":"Tax","kw":["gst", "tax invoice", "tax return"]},
            {"domain":"Legal","category":"Contract","kw":["non-disclosure agreement", "nda", "consulting agreement", "employment agreement"]},
        ]

        for rule in rules:
            # Check both text and filename for the keyword
            if any(k in text_lower or k in filename_lower for k in rule["kw"]):
                return {
                    "domain": rule["domain"],
                    "category": rule["category"],
                    "file_extension": ext or "files",
                    "confidence": 0.95,
                    "domain_score": 100,
                    "category_score": 100,
                }

        # Extension-based code file classification
        CODE_EXTENSIONS = {
            'py', 'js', 'jsx', 'ts', 'tsx', 'java', 'cpp', 'c', 'h', 'hpp',
            'cs', 'go', 'rs', 'rb', 'php', 'swift', 'kt', 'scala',
            'sh', 'bash', 'ps1', 'bat', 'cmd', 'sql', 'r', 'dart', 'lua'
        }
        
        if ext in CODE_EXTENSIONS:
            # Determine subcategory based on extension
            frontend_exts = {'js', 'jsx', 'ts', 'tsx', 'html', 'css', 'scss', 'sass', 'vue'}
            backend_exts = {'py', 'java', 'go', 'php', 'rb', 'rs', 'cs'}
            
            if ext in frontend_exts:
                category = "Frontend"
            elif ext in backend_exts:
                category = "Backend"
            else:
                category = "Script"
                
            return {
                "domain": "Code",
                "category": category,
                "file_extension": ext,
                "confidence": 0.95,
                "domain_score": 100,
                "category_score": 100,
            }

        # Extension-based documentation hint
        if ext in {"md","rst","adoc"}:
            return {
                "domain": "Documentation",
                "category": "Other",
                "file_extension": ext or "files",
                "confidence": 0.85,
                "domain_score": 90,
                "category_score": 90,
            }

        return None

    # Category-level keywords for each domain (Expanded)
    CATEGORY_KEYWORDS_BY_DOMAIN = {
        "Technology": {
            "UAV": ["uav", "drone", "unmanned aerial", "unmanned", "quadcopter", "hexacopter", "flight"],
            "Web": ["web", "website", "web app", "web application", "web development", "full stack"],
            "Database": ["database", "sql", "nosql", "mongodb", "postgres", "mysql", "redis"],
            "API": ["api", "endpoint", "rest", "graphql", "grpc", "swagger", "openapi"],
            "DevOps": ["docker", "kubernetes", "ci/cd", "jenkins", "terraform", "ansible", "cloud"],
            "AI": ["artificial intelligence", "ai", "machine learning", "deep learning", "llm", "neural network"],
            "Security": ["security", "encryption", "ssl", "tls", "auth", "firewall", "cyber", "cipher", "crypto", "aes", "rsa"],
            "Mobile": ["mobile", "ios", "android", "flutter", "react native", "app"],
            "Other": []
        },
        "Code": {
            "Backend": ["backend", "server", "api", "database", "express", "django", "flask", "spring", "sql"],
            "Frontend": ["frontend", "ui", "react", "vue", "angular", "html", "css", "component"],
            "Algorithm": ["algorithm", "data structure", "sorting", "searching", "graph", "tree"],
            "Testing": ["test", "unit test", "integration test", "jest", "pytest", "coverage"],
            "Other": []
        },
        "Finance": {
            "Accounting": ["accounting", "ledger", "audit", "balance sheet", "p&l"],
            "Payroll": ["payroll", "salary", "wage", "slip", "compensation"],
            "Tax": ["tax", "gst", "itr", "return", "filing"],
            "Investment": ["investment", "stock", "portfolio", "mutual fund", "equity"],
            "Other": []
        },
        "Education": {
            "Programming": ["programming", "python", "java", "code", "development"],
            "Mathematics": ["math", "algebra", "calculus", "statistics", "geometry"],
            "Science": ["physics", "chemistry", "biology", "science"],
            "DataScience": ["data science", "ml", "analysis", "pandas", "numpy"],
            "Other": []
        },
        "College": {
            "Admin": ["transcript", "degree", "certificate", "bonafide", "fee receipt"],
            "Placement": ["placement", "internship", "job offer", "recruiting", "campus drive"],
            "Academic": ["course", "syllabus", "project", "assignment", "thesis"],
            "Clubs": ["club", "event", "fest", "competition", "workshop"],
            "Other": []
        },
        "School": {
            "Admin": ["report card", "result", "leaving certificate", "bonafide", "calendar"],
            "Academic": ["homework", "worksheet", "assignment", "exam", "quiz"],
            "Events": ["annual day", "sports day", "field trip", "picnic"],
            "Other": []
        },
        "Company": {
            "Product": ["prd", "product", "requirements", "roadmap", "user story", "backlog"],
            "Service": ["sow", "proposal", "agreement", "sla", "deliverable", "contract"],
            "HR": ["offer letter", "appointment letter", "appraisal", "policy", "handbook"],
            "Legal": ["nda", "non-disclosure", "contract", "partnership"],
            "Finance": ["invoice", "quote", "po", "purchase order", "budget"],
            "Other": []
        },
        "Healthcare": {
            "Clinical": ["prescription", "discharge", "opd", "admission", "case paper"],
            "LabReport": ["report", "test result", "blood", "urine", "pathology"],
            "Imaging": ["x-ray", "mri", "abdo", "scan", "usg", "sonography"],
            "Insurance": ["claim", "insurance", "tpa", "approval", "cashless"],
            "Other": []
        },
        "Personal": {
            "Identity": ["resume", "cv", "biodata", "id proof", "address proof"],
            "Bills": ["electricity", "gas", "water", "bill", "maintenance"],
            "Financial": ["bank statement", "passbook", "credit card", "loan"],
            "Housing": ["rent agreement", "possession", "allotment", "deed"],
            "Other": []
        },
        "Government": {
            "ID": ["aadhaar", "pan", "passport", "license", "voter"],
            "Tax": ["itr", "form 16", "income tax", "acknowledgement"],
            "Legal": ["affidavit", "agreement", "power of attorney", "deed"],
            "Other": []
        },
        "Legal": {
            "Contract": ["contract", "agreement", "mou", "nda"],
            "Property": ["lease", "deed", "sale", "rent"],
            "Court": ["order", "judgment", "petition", "notice"],
            "Other": []
        },
        "Business": {
            "Strategy": ["strategy", "plan", "deck", "presentation"],
            "Marketing": ["campaign", "brochure", "flyer", "social media"],
            "Sales": ["pipeline", "lead", "proposal", "quote"],
            "Other": []
        },
        "ResearchPaper": {
            "Other": []  # Usually flat structure
        },
        "Documentation": {
            "Other": []
        }
    }
    
    def classify_hierarchical(self, text: str, filename: str = "") -> Dict[str, str]:
        """Classify content into hierarchical structure: Domain > Category > FileType
        
        Args:
            text: Document content to classify
            filename: Original filename (used for additional context)
            
        Returns:
            Dictionary with keys: domain, category, file_extension
            Example: {"domain": "Technology", "category": "UAV", "file_extension": "pptx"}
        """
        try:
            text_lower = text.lower()
            filename_lower = filename.lower()

            # Apply guardrail rules (broad coverage for major types)
            forced = self._guardrail_classify(text_lower, filename_lower, filename)
            if forced:
                return forced
            
            # Extract file extension
            file_ext = ""
            if "." in filename:
                file_ext = filename.rsplit(".", 1)[-1].lower()
            
            # Step 1: Classify domain using keyword scoring
            domain_scores = {}
            for domain, keywords in self.DOMAIN_KEYWORDS.items():
                score = 0
                # Count strong keywords (2x weight)
                for keyword in keywords["strong"]:
                    score += text_lower.count(keyword) * 2
                # Count weak keywords (1x weight)
                for keyword in keywords["weak"]:
                    score += text_lower.count(keyword) * 1
                # Filename bonus (5x weight)
                for keyword in keywords["strong"]:
                    if keyword in filename_lower:
                        score += 5
                domain_scores[domain] = score
            
            # Select best domain (default to Technology if no matches)
            best_domain = max(domain_scores, key=domain_scores.get) or "Technology"
            if domain_scores[best_domain] == 0:
                best_domain = "Technology"
            
            logger.info(f"Domain classified: {best_domain} (score: {domain_scores[best_domain]})")
            best_domain_score = domain_scores[best_domain]
            
            # Step 2: Classify category within domain
            category_keywords = self.CATEGORY_KEYWORDS_BY_DOMAIN.get(best_domain, {})
            category_scores = {}
            
            for category, keywords in category_keywords.items():
                if category == "Other":
                    continue
                # Sum keyword matches in text
                score = sum(text_lower.count(kw) for kw in keywords)
                # Filename bonus
                score += sum(5 for kw in keywords if kw in filename_lower)
                category_scores[category] = score
            
            # Select best category (default to Other if no matches)
            best_category = max(category_scores, key=category_scores.get) if category_scores else "Other"
            if category_scores.get(best_category, 0) == 0:
                best_category = "Other"
            
            logger.info(f"Category classified: {best_category} (score: {category_scores.get(best_category, 0)})")
            best_category_score = category_scores.get(best_category, 0)
            
            # Calculate category confidence (normalized 0-1)
            total_category_score = sum(category_scores.values())
            category_confidence = best_category_score / total_category_score if total_category_score > 0 else 0
            
            # Calculate domain confidence
            total_domain_score = sum(domain_scores.values())
            domain_confidence = best_domain_score / total_domain_score if total_domain_score > 0 else 0
            
            # Combined confidence (weighted: domain 60%, category 40%)
            combined_confidence = round(min(1.0, (domain_confidence * 0.6) + (category_confidence * 0.4)), 2)
            
            logger.info(f"Confidence - Domain: {domain_confidence:.2f}, Category: {category_confidence:.2f}, Combined: {combined_confidence}")
            
            return {
                "domain": best_domain,
                "category": best_category,
                "file_extension": file_ext or "files",
                "confidence": combined_confidence,
                "domain_score": best_domain_score,
                "category_score": best_category_score
            }
        
        except Exception as e:
            logger.error(f"Error in hierarchical classification: {e}")
            return {
                "domain": "Technology",
                "category": "Other",
                "file_extension": file_ext or "files",
                "confidence": 0.0,
                "domain_score": 0,
                "category_score": 0
            }
