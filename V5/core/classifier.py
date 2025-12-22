"""Hierarchical document classification system - Domain → Category → FileType"""
import logging
from typing import Dict

logger = logging.getLogger(__name__)


class DocumentClassifier:
    """Handles hierarchical document classification with scaled keyword system"""
    
    # Domain-level keywords (14 domains with 70-100+ keywords each)
    DOMAIN_KEYWORDS = {
        "Technology": {
            "strong": ["uav", "drone", "robot", "robotics", "unmanned", "quadcopter", "hexacopter", "flight",
                      "web application", "website", "web development", "web design",
                      "cloud computing", "cloud infrastructure", "devops", "docker", "kubernetes", 
                      "aws", "azure", "gcp", "cloud platform", "serverless",
                      "database architecture", "data warehouse", "nosql", "mongodb", "postgres", "mysql", "redis", "elasticsearch",
                      "api architecture", "rest api", "api design", "api development",
                      "infrastructure", "infrastructure as code", "terraform", "ansible",
                      "ssl", "tls", "certificate", "encryption", "authentication protocol", "authorization",
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
                      "expense", "expense report", "reimbursement", "invoice", "invoice", "receipt",
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
                      "gpa", "grade point average", "transcript", "transcript request", "diploma",
                      "alumni", "alumnus", "alumna", "graduate", "commencement", "graduation",
                      "fraternity", "sorority", "greek life", "greek organization", "pledge",
                      "club", "organization", "student organization", "student group", "group",
                      "student government", "senate", "council", "board", "president", "vice president",
                      "registration", "course registration", "add drop", "course schedule",
                      "professor", "instructor", "faculty", "staff", "administrator", "dean",
                      "campus life", "student life", "residential life", "community",
                      "event", "conference", "seminar", "networking", "career fair", "recruiting"],
            "weak": ["college", "university", "student", "campus", "academic"]
        },
        "School": {
            "strong": ["elementary", "elementary school", "middle school", "high school", "secondary",
                      "k-12", "k12", "public school", "private school", "charter school",
                      "grade", "grade level", "grade 1", "grade 2", "grade 3", "grade 4", "grade 5",
                      "classroom", "class", "period", "period", "lunch", "lunch period", "recess",
                      "teacher", "principal", "staff", "counselor", "nurse", "aide", "administrator",
                      "report card", "progress report", "behavior", "discipline", "detention",
                      "assignment", "homework", "worksheet", "project", "presentation", "poster",
                      "exam", "test", "quiz", "mid-term", "final exam", "standardized test",
                      "schedule", "timetable", "class schedule", "bell schedule", "calendar",
                      "parent", "guardian", "parent teacher conference", "ptc", "pta", "pto",
                      "activity", "club", "sports", "athletics", "team", "game", "tournament",
                      "field trip", "assembly", "pep rally", "graduation", "commencement",
                      "library", "media center", "cafeteria", "gymnasium", "auditorium", "lab"],
            "weak": ["school", "education", "student", "learning", "teaching"]
        },
        "Company": {
            "strong": ["employee", "employees", "staff", "team", "department", "division", "unit",
                      "project", "initiative", "program", "campaign", "strategy", "strategic",
                      "budget", "budgeting", "forecast", "planning", "deadline", "timeline",
                      "product", "product line", "product development", "roadmap", "feature",
                      "service", "service offering", "service delivery", "support", "customer support",
                      "client", "customer", "vendor", "partner", "stakeholder", "supplier",
                      "human resources", "hr", "recruitment", "hiring", "recruitment", "onboarding",
                      "payroll", "compensation", "salary", "bonus", "incentive", "performance review",
                      "meeting", "standup", "sync", "all hands", "all-hands", "town hall",
                      "presentation", "pitch", "demo", "prototype", "mockup", "wireframe",
                      "quarterly", "q1", "q2", "q3", "q4", "quarter", "fiscal quarter",
                      "annual", "annual report", "earnings", "revenue", "profit", "financial statement",
                      "performance", "performance metric", "kpi", "key performance indicator",
                      "review", "performance review", "feedback", "evaluation", "assessment",
                      "office", "workspace", "workplace", "remote", "hybrid", "in-office",
                      "company culture", "values", "mission", "vision", "company policy",
                      "business plan", "business model", "business development", "sales", "marketing"],
            "weak": ["company", "work", "business", "job", "employment", "workplace"]
        },
        "Healthcare": {
            "strong": ["patient", "patients", "medical", "medicine", "physician", "doctor", "healthcare",
                      "hospital", "clinic", "medical center", "urgent care", "emergency", "er", "icu",
                      "diagnosis", "diagnostic", "symptom", "treatment", "therapy", "clinical",
                      "prescription", "medication", "pharmaceutical", "drug", "vaccine", "immunization",
                      "disease", "illness", "condition", "disorder", "syndrome", "diagnosis",
                      "vital signs", "blood pressure", "heart rate", "temperature", "pulse",
                      "surgery", "surgical", "operating room", "anesthesia", "post-operative", "recovery",
                      "radiology", "x-ray", "ct scan", "mri", "ultrasound", "imaging",
                      "laboratory", "lab test", "blood test", "pathology", "specimen",
                      "nursing", "nurse", "icu nurse", "registered nurse", "lpn", "nursing home",
                      "therapy", "physical therapy", "occupational therapy", "speech therapy",
                      "mental health", "psychiatry", "psychiatric", "psychology", "psychologist",
                      "pediatric", "pediatrician", "geriatric", "geriatrician", "maternal",
                      "dicom", "hl7", "hl-7", "medical imaging", "medical record", "emr", "ehr"],
            "weak": ["health", "medicine", "doctor", "medical", "care", "patient"]
        },
        "Legal": {
            "strong": ["contract", "agreement", "legal agreement", "terms", "terms and conditions",
                      "clause", "section", "article", "amendment", "addendum", "appendix",
                      "party", "parties", "plaintiff", "defendant", "litigant", "attorney",
                      "law", "legal", "statute", "regulation", "ordinance", "compliance",
                      "copyright", "patent", "trademark", "intellectual property", "ip", "licensing",
                      "liability", "indemnity", "indemnification", "insurance", "coverage",
                      "court", "lawsuit", "litigation", "legal action", "legal proceeding", "trial",
                      "jurisdiction", "jurisdiction", "venue", "governing law", "arbitration",
                      "herein", "hereby", "whereas", "whereas", "pursuant to", "in accordance with",
                      "efective date", "term", "termination", "breach", "breach of contract",
                      "damages", "remedy", "remedies", "injunction", "relief", "specific performance",
                      "warrant", "warranty", "represent", "representation", "covenant"],
            "weak": ["legal", "law", "attorney", "lawyer", "rights", "contract"]
        },
        "Business": {
            "strong": ["strategy", "strategic plan", "business model", "value proposition",
                      "marketing", "marketing strategy", "advertising", "campaign", "promotion",
                      "sales", "sales strategy", "sales pipeline", "customer acquisition",
                      "customer", "customer experience", "customer service", "customer retention",
                      "market", "market share", "market analysis", "competitive analysis", "competitor",
                      "growth", "growth strategy", "expansion", "scaling", "scale", "enterprise",
                      "operations", "operational", "operational efficiency", "supply chain",
                      "management", "leadership", "leader", "executive", "ceo", "cfo", "cto",
                      "organization", "organizational", "team structure", "hierarchy",
                      "planning", "objective", "goal", "milestone", "target", "kpi",
                      "innovation", "disruptive", "disruption", "new product", "new service"],
            "weak": ["business", "company", "plan", "goal", "strategy", "work"]
        },
        "ResearchPaper": {
            "strong": ["abstract", "introduction", "methodology", "results", "conclusion", "references",
                      "research", "study", "analysis", "experiment", "experimental", "empirical",
                      "hypothesis", "hypothesis test", "hypothesis testing", "statistical test",
                      "data", "data analysis", "statistical analysis", "qualitative", "quantitative",
                      "literature review", "literature", "citation", "cite", "reference",
                      "author", "researcher", "academic", "scholar", "institution",
                      "journal", "journal article", "peer review", "peer reviewed", "publication",
                      "conference", "conference paper", "symposium", "workshop",
                      "figure", "table", "graph", "chart", "diagram", "visualization",
                      "et al", "et al.", "doi", "isbn", "issn", "arxiv"],
            "weak": ["research", "paper", "academic", "study", "analysis"]
        },
        "Documentation": {
            "strong": ["## ", "# ", "api", "api documentation", "endpoint", "endpoint",
                      "parameter", "parameters", "argument", "argument list",
                      "response", "response code", "response body", "response header",
                      "schema", "json schema", "data schema", "data model",
                      "authentication", "authorization", "oauth", "api key", "bearer",
                      "rest", "restful", "rest api", "http", "http method", "get", "post", "put", "delete",
                      "swagger", "openapi", "openapi specification", "raml", "api blueprint",
                      "example", "usage example", "sample", "sample code", "code snippet",
                      "guide", "getting started", "quick start", "installation", "setup",
                      "tutorial", "walkthrough", "step by step", "step-by-step"],
            "weak": ["help", "explain", "guide", "reference", "documentation", "doc"]
        }
    }
    
    def _guardrail_classify(self, text_lower: str, filename_lower: str, filename: str):
        """Apply explicit guardrail rules to prevent obvious misclassifications.
        Returns a forced classification dict or None.
        """
        ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''

        # Rules ordered by specificity and risk of misclassification
        rules = [
            # Technology
            {"domain":"Technology","category":"UAV","kw":["uav","drone","quadcopter","aerial"]},
            {"domain":"Technology","category":"API","kw":["openapi","swagger","graphql","grpc","raml","api gateway","rest api","api documentation","http method","endpoints"]},
            {"domain":"Technology","category":"DevOps","kw":["docker","kubernetes","k8s","jenkins","terraform","ansible","helm","github actions","gitlab ci","ci/cd","cicd"]},
            {"domain":"Technology","category":"Database","kw":["postgres","mysql","mongodb","redis","elasticsearch","dynamodb","cassandra","database","sql"],},
            {"domain":"Technology","category":"Security","kw":["encryption","ssl","tls","certificate","oauth","jwt","firewall","penetration test","xss","csrf","aes","rsa","hashing"]},
            {"domain":"Technology","category":"Mobile","kw":["android","ios","flutter","react native","xcode","apk","ipa","swift","kotlin"]},
            {"domain":"Technology","category":"Cloud","kw":["aws","azure","gcp","lambda","s3","cloudformation","ec2","iam","gke","aks","app service","functions"]},

            # Code
            {"domain":"Code","category":"Frontend","kw":["react","jsx","tsx","nextjs","component","usestate","useeffect","<html","<div","<body","<!doctype","tailwind","redux","vue","angular"]},
            {"domain":"Code","category":"Backend","kw":["api","endpoint","route","middleware","controller","express","django","flask","fastapi","spring","server","http","request","response","jwt","orm"]},
            {"domain":"Code","category":"Algorithm","kw":["algorithm","sorting","binary search","time complexity","big o","graph","dynamic programming","quicksort","mergesort"]},
            {"domain":"Code","category":"Testing","kw":["pytest","unittest","jest","mocha","vitest","test case","assert","mock","coverage","tdd","bdd"]},

            # Finance
            {"domain":"Finance","category":"Payroll","kw":["payroll","salary","wage","compensation","deduction","withholding"]},
            {"domain":"Finance","category":"Accounting","kw":["ledger","balance sheet","trial balance","accounts payable","accounts receivable","audit","ifrs","gaap"]},
            {"domain":"Finance","category":"Investment","kw":["portfolio","stock","dividend","equity","roi","bond","mutual fund","etf"]},
            {"domain":"Finance","category":"Tax","kw":["tax","gst","vat","irs","filing","deduction"]},
            {"domain":"Finance","category":"Expense","kw":["expense report","reimbursement","receipt","invoice","opex","capex"]},
            {"domain":"Finance","category":"Budget","kw":["budget","forecast","planning","variance","allocation"]},
            {"domain":"Finance","category":"Maintenance","kw":["maintenance","repair","upkeep"]},

            # Healthcare & Legal
            {"domain":"Healthcare","category":"Other","kw":["patient","diagnosis","treatment","x-ray","mri","ct scan","clinical","hospital","prescription","medication","therapy"]},
            {"domain":"Legal","category":"Other","kw":["contract","agreement","clause","liability","jurisdiction","indemnity","compliance","statute","copyright","patent","trademark","terms and conditions"]},

            # Research & Documentation
            {"domain":"ResearchPaper","category":"Other","kw":["abstract","introduction","methodology","results","doi","issn","arxiv","et al","peer review","journal"]},
            {"domain":"Documentation","category":"Other","kw":["swagger","openapi","raml","api documentation","specification","parameters","request body","response body","getting started","installation","quick start","readme"]},

            # Education, College, School
            {"domain":"Education","category":"Mathematics","kw":["calculus","algebra","geometry","statistics","probability","linear algebra"]},
            {"domain":"Education","category":"DataScience","kw":["pandas","numpy","scikit-learn","sklearn","tensorflow","pytorch","keras","neural network","dataset","model training","inference"]},
            {"domain":"Education","category":"Science","kw":["physics","chemistry","biology","geology","astronomy"]},
            {"domain":"Education","category":"Other","kw":["assignment","homework","syllabus","curriculum","quiz","lecture","semester"]},
            {"domain":"College","category":"Clubs","kw":["club","fraternity","sorority","greek life","pledge"]},
            {"domain":"College","category":"Other","kw":["university","campus","scholarship","dormitory","degree"]},
            {"domain":"School","category":"Assignments","kw":["assignment","homework","worksheet","project"]},

            # Company & Business
            {"domain":"Company","category":"Product","kw":["product","roadmap","feature","specification","requirements"]},
            {"domain":"Company","category":"HR","kw":["hiring","recruitment","onboarding","employee","training"]},
            {"domain":"Company","category":"Marketing","kw":["marketing","campaign","brand","promotion"]},
            {"domain":"Business","category":"Other","kw":["strategy","market analysis","competitive analysis","kpi","business model"]},
        ]

        for rule in rules:
            if any(k in text_lower or k in filename_lower for k in rule["kw"]):
                return {
                    "domain": rule["domain"],
                    "category": rule["category"],
                    "file_extension": ext or "files",
                    "confidence": 0.9 if rule["domain"] != "Technology" or rule["category"] != "UAV" else 0.95,
                    "domain_score": 95 if rule["domain"] != "Technology" or rule["category"] != "UAV" else 100,
                    "category_score": 95 if rule["domain"] != "Technology" or rule["category"] != "UAV" else 100,
                }

        # Extension-based documentation hint (applied only if no rule matched)
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

    # Category-level keywords for each domain (40+ subcategories)
    CATEGORY_KEYWORDS_BY_DOMAIN = {
        "Technology": {
            "UAV": ["uav", "drone", "unmanned aerial", "unmanned", "quadcopter", "hexacopter", 
                   "flight", "airborne", "aerial", "aircraft", "aeroplane"],
            "Web": ["web", "website", "web app", "web application", "web development", "web design",
                   "html", "css", "javascript", "react", "vue", "angular", "svelte"],
            "Database": ["database", "sql", "nosql", "relational", "mongodb", "postgres", "mysql",
                        "elasticsearch", "redis", "cassandra", "dynamodb", "data warehouse"],
            "API": ["api", "endpoint", "rest", "rest api", "graphql", "grpc", "websocket",
                   "swagger", "openapi", "api gateway", "microservice"],
            "DevOps": ["docker", "kubernetes", "ci/cd", "cicd", "deployment", "jenkins", "gitlab ci",
                      "github actions", "terraform", "ansible", "puppet", "chef", "infrastructure"],
            "AI": ["artificial intelligence", "ai", "neural network", "deep learning", "machine learning",
                  "llm", "large language model", "gpt", "bert", "transformer"],
            "Cloud": ["aws", "azure", "gcp", "cloud", "serverless", "lambda", "cloudformation",
                     "elastic", "rds", "s3", "cloudstorage"],
            "Security": ["security", "encryption", "ssl", "tls", "certificate", "authentication",
                        "authorization", "oauth", "jwt", "firewall", "penetration test"],
            "Mobile": ["mobile", "ios", "android", "flutter", "react native", "xamarin", "app development"],
            "Other": []
        },
        "Code": {
            "Backend": ["backend", "api", "rest api", "endpoint", "route", "handler", "middleware",
                       "database", "db", "query", "sql", "orm", "nosql", "async", "await",
                       "server", "server-side", "service", "api service", "microservice",
                       "nodejs", "express", "django", "flask", "fastapi", "spring", "java",
                       "def ", "class ", "function", "method", "module", "package",
                       "authentication", "authorization", "authentication", "session", "jwt", "token",
                       "request", "response", "http", "http method", "get", "post", "put", "delete",
                       "error handling", "exception", "logging", "logger", "debug",
                       "data persistence", "persistence", "cache", "redis", "memcached",
                       "api documentation", "swagger", "openapi", "postman", "insomnia"],
            "Frontend": ["frontend", "react", "vue", "angular", "svelte", "nextjs", "nuxt",
                        "jsx", "tsx", "javascript", "typescript", "html", "css",
                        "<div", "<html", "<head", "<body", "<!doctype", "<!DOCTYPE",
                        "component", "hook", "useState", "useEffect", "props",
                        "dom", "dom manipulation", "event listener", "event handler",
                        "state", "state management", "redux", "vuex", "pinia",
                        "css", "sass", "scss", "styled-components", "tailwind",
                        "render", "virtual dom", "reconciliation", "lifecycle",
                        "form", "input", "validation", "user interface", "ui"],
            "Algorithm": ["algorithm", "data structure", "sorting", "searching", "recursion",
                         "array", "linked list", "tree", "graph", "binary search", "dynamic programming",
                         "time complexity", "space complexity", "big o", "optimization",
                         "quicksort", "mergesort", "bubblesort", "heapsort", "insertionsort",
                         "bfs", "dfs", "dijkstra", "traversal", "stack", "queue"],
            "Testing": ["test", "unit test", "integration test", "e2e test", "test case", "testing",
                       "assert", "expect", "mock", "stub", "spy", "jasmine", "jest", "pytest", "unittest",
                       "mocha", "chai", "vitest", "coverage", "test coverage",
                       "tdd", "test driven development", "bdd", "behavior driven development"],
            "Other": []
        },
        "Finance": {
            "Accounting": ["accounting", "audit", "auditor", "ledger", "journal", "trial balance",
                          "general ledger", "accounts payable", "accounts receivable"],
            "Payroll": ["payroll", "salary", "wage", "employee", "deduction", "withholding",
                       "compensation", "benefits", "bonus", "incentive"],
            "Maintenance": ["maintenance", "repair", "maintenance cost", "upkeep", "capital maintenance",
                           "preventive maintenance", "corrective maintenance"],
            "Budget": ["budget", "budgeting", "forecast", "forecasting", "planning", "financial planning"],
            "Investment": ["investment", "portfolio", "stock", "dividend", "roi", "return on investment",
                          "bond", "equity", "asset allocation"],
            "Expense": ["expense", "expense report", "cost", "operating expense", "capital expense",
                       "reimbursement", "receipt"],
            "Tax": ["tax", "taxation", "tax return", "irs", "deduction", "filing", "deadline"],
            "Other": []
        },
        "Education": {
            "Programming": ["programming", "code", "python", "java", "javascript", "c++", "c#",
                           "algorithm", "data structure", "coding", "software development"],
            "Mathematics": ["math", "calculus", "algebra", "geometry", "statistics", "probability",
                           "linear algebra", "discrete math", "number theory"],
            "Science": ["physics", "chemistry", "biology", "science", "geology", "astronomy",
                       "organic chemistry", "biochemistry"],
            "Literature": ["literature", "writing", "essay", "poetry", "novel", "short story",
                          "drama", "composition", "creative writing"],
            "History": ["history", "date", "event", "era", "century", "historical", "ancient",
                       "medieval", "modern", "contemporary"],
            "Languages": ["language", "english", "spanish", "french", "german", "chinese",
                         "arabic", "japanese", "korean", "linguistics"],
            "DataScience": ["data science", "machine learning", "deep learning", "neural network",
                           "numpy", "pandas", "sklearn", "scikit-learn", "tensorflow", "pytorch",
                           "data analysis", "statistics", "statistical", "predictive", "classification",
                           "regression", "clustering", "supervised learning", "unsupervised learning"],
            "Other": []
        },
        "College": {
            "Clubs": ["club", "organization", "student organization", "fraternity", "sorority",
                     "greek life", "pledge", "group", "community"],
            "Courses": ["course", "syllabus", "course syllabus", "course schedule", "schedule",
                       "enrollment", "prerequisites", "course description"],
            "Events": ["event", "conference", "seminar", "networking", "career fair", "meeting",
                      "workshop", "symposium"],
            "Administration": ["registration", "course registration", "transcript", "degree",
                              "enrollment", "add drop", "tuition"],
            "Other": []
        },
        "School": {
            "Assignments": ["assignment", "homework", "worksheet", "project", "presentation",
                           "poster", "lab", "experiment"],
            "Schedule": ["schedule", "timetable", "class time", "period", "bell schedule",
                        "class schedule", "calendar"],
            "Events": ["event", "field trip", "assembly", "pep rally", "game", "tournament",
                      "graduation", "commencement"],
            "Administration": ["grade", "report card", "discipline", "detention", "behavior",
                              "progress report", "academic record"],
            "Other": []
        },
        "Company": {
            "Product": ["product", "product line", "product development", "roadmap", "feature",
                       "release", "specification", "requirements", "product management"],
            "Service": ["service", "service offering", "service delivery", "support",
                       "customer support", "technical support", "support ticket"],
            "HR": ["employee", "recruitment", "hiring", "recruitment", "onboarding", "training",
                  "professional development", "career development"],
            "Finance": ["budget", "budgeting", "forecast", "expense", "revenue", "cost",
                       "financial planning", "financial analysis"],
            "Marketing": ["marketing", "marketing strategy", "campaign", "advertisement",
                         "brand", "branding", "promotion", "customer acquisition"],
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
